"""Deterministic herb-drug interaction evaluator.

The rules engine is the binding safety layer. It is pure, auditable and fully
testable: same inputs -> same DecisionSet. The LLM never participates in a
safety decision here.
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from .constants import (
    DRUG_CLASSES,
    POLYPHARMACY_ESCALATE_COUNT,
    SEVERITY_BLOCK,
    SEVERITY_CAUTION,
)
from .decision import Decision, ReasonCode
from .models import InteractionRule
from .severity import Evidence, Severity

_UNKNOWN = "unknown"


@dataclass
class Match:
    rule_id: int | None
    pair: str
    severity: str
    evidence: str
    decision: str
    reason_code: str
    recommendation: str = ""


@dataclass
class DecisionSet:
    overall: str = "pass"
    reason_code: str = ReasonCode.NO_RULE
    matches: list[Match] = field(default_factory=list)
    entities: dict = field(default_factory=dict)
    engine_version: str = "1.0.0"

    @property
    def blocked(self) -> bool:
        return self.overall == Decision.BLOCK.label


def _severity_enum(name: str) -> Severity:
    return Severity[name.upper()]


def _evidence_enum(name: str) -> Evidence:
    return Evidence[name.upper()]


def _dose_mg(dose: str | None) -> float | None:
    """Parse a dose string like '5 mg' or '1 tsp' -> mg number if numeric."""
    if not dose:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", dose)
    return float(m.group(1)) if m else None


def _below_dose_threshold(rule: InteractionRule, herb: str, doses: dict) -> bool:
    """Dose-aware skip: culinary doses never trigger therapeutic rules."""
    dose = doses.get(herb) or doses.get(rule.herb_a)
    mg = _dose_mg(dose)
    if mg is None:
        return False
    threshold = _dose_mg(rule.dose_threshold) if rule.dose_threshold else None
    return threshold is not None and mg < threshold


def _evaluate_rule(rule: InteractionRule, pair: str) -> Match:
    severity = _severity_enum(rule.severity)
    evidence = _evidence_enum(rule.evidence)

    if evidence in (Evidence.CLASSICAL, Evidence.ANECDOTAL):
        decision, reason = Decision.CAUTION, ReasonCode.CLASSICAL_CAUTION
    elif severity in SEVERITY_BLOCK:
        decision = Decision.BLOCK
        if severity.value >= Severity.HIGH.value:
            reason = ReasonCode.INTERACTION_HIGH
        else:
            reason = ReasonCode.INTERACTION_MODERATE
    elif severity in SEVERITY_CAUTION:
        decision, reason = Decision.CAUTION, ReasonCode.INTERACTION_LOW
    else:
        decision, reason = Decision.NEEDS_REVIEW, ReasonCode.NOVEL_PAIR

    return Match(
        rule_id=rule.pk,
        pair=pair,
        severity=rule.severity,
        evidence=rule.evidence,
        decision=decision.label,
        reason_code=reason,
        recommendation=rule.recommendation,
    )


def evaluate(
    herbs: list[str],
    drugs: list[str],
    context: dict | None = None,
    doses: dict | None = None,
    rules: Iterable[InteractionRule] | None = None,
    ambiguous: list[str] | None = None,
) -> DecisionSet:
    """Core evaluation. Raises nothing - always returns a DecisionSet.

    Passed a generator of rules so callers control persistence (tests inject
    factories; production uses the DB).
    """
    herbs = [h.lower() for h in herbs]
    drugs = [d.lower() for d in drugs]
    context = context or {}
    doses = doses or {}
    ambiguous = ambiguous or []
    expanded_drugs = set(drugs) | {c for d in drugs for c in DRUG_CLASSES.get(d, ())}
    all_subs = set(herbs) | expanded_drugs

    rules = rules if rules is not None else InteractionRule.objects.filter(active=True)
    result = DecisionSet(entities={"herbs": herbs, "drugs": drugs})

    for rule in rules:
        rb = rule.herb_a.lower()
        rpair = (rule.herb_b_or_drug or "").lower()
        matched = False
        pair = ""

        if rule.context_tag:
            # context-specific rule (e.g. pregnancy): fires on herb presence + flag
            flag = rule.context_tag
            if rb in herbs and bool(context.get(flag)):
                matched, pair = True, f"{rb} (context: {flag})"
        elif rb in herbs and (rpair in all_subs):
            matched, pair = True, f"{rb} <-> {rpair}"
        elif rb in drugs and (rpair in all_subs):
            matched, pair = True, f"{rb} <-> {rpair}"

        if not matched:
            continue
        if _below_dose_threshold(rule, rb, doses):
            continue
        result.matches.append(_evaluate_rule(rule, pair))

    # Polypharmacy aggregation: compounding of 2+ moderate/higher matches.
    compounding = [m for m in result.matches if _severity_enum(m.severity) in SEVERITY_BLOCK]
    if len(compounding) >= POLYPHARMACY_ESCALATE_COUNT:
        return DecisionSet(
            overall=Decision.BLOCK.label,
            reason_code=ReasonCode.POLYPHARMACY,
            matches=result.matches,
            entities=result.entities,
            engine_version=result.engine_version,
        )

    if result.matches:
        order = {m.decision: Decision[m.decision.upper()].value for m in result.matches}
        worst = max(order.items(), key=lambda kv: kv[1])
        return DecisionSet(
            overall=worst[0],
            reason_code=ReasonCode.NO_RULE,
            matches=result.matches,
            entities=result.entities,
            engine_version=result.engine_version,
        )

    # No rule fired.
    if ambiguous:
        return DecisionSet(
            overall=Decision.NEEDS_REVIEW.label,
            reason_code=ReasonCode.ENTITY_AMBIGUOUS,
            entities=result.entities,
            engine_version=result.engine_version,
        )
    if herbs and drugs:
        return DecisionSet(
            overall=Decision.NEEDS_REVIEW.label,
            reason_code=ReasonCode.NOVEL_PAIR,
            entities=result.entities,
            engine_version=result.engine_version,
        )
    return DecisionSet(
        overall=Decision.PASS.label,
        reason_code=ReasonCode.NO_RULE,
        entities=result.entities,
        engine_version=result.engine_version,
    )


def fail_closed(error: Exception) -> DecisionSet:
    """Any engine/DB/parse error must fail closed - never silently pass."""
    return DecisionSet(
        overall="needs_review",
        reason_code=ReasonCode.ENGINE_ERROR,
        entities={"error": str(error)[:200]},
        engine_version="error",
    )
