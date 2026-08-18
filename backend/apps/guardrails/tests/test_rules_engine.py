"""Rules-engine tests. Injects rules directly - no DB needed.

Safety properties under test:
- classical/anecdotal evidence NEVER blocks (CAUTION at most)
- errors fail closed to NEEDS_REVIEW
- ambiguity and novel pairs never silently pass
"""

from apps.guardrails.decision import ReasonCode
from apps.guardrails.models import InteractionRule
from apps.guardrails.rules_engine import evaluate, fail_closed


def rule(herb_a, herb_b_or_drug="", *, severity="HIGH", evidence="MODERATE", context_tag="", dose_threshold=""):
    return InteractionRule(
        herb_a=herb_a,
        herb_b_or_drug=herb_b_or_drug,
        severity=severity,
        evidence=evidence,
        recommendation="Consult a practitioner.",
        dose_threshold=dose_threshold,
        context_tag=context_tag,
        active=True,
    )


def test_empty_input_passes():
    result = evaluate([], [], {}, rules=[])
    assert result.overall == "pass"
    assert not result.matches


def test_novel_herb_drug_pair_never_passes():
    result = evaluate(["ashwagandha"], ["warfarin"], {}, rules=[])
    assert result.overall == "needs_review"
    assert result.reason_code == ReasonCode.NOVEL_PAIR


def test_ambiguous_entity_never_passes():
    result = evaluate([], [], {}, ambiguous=["ashwagandha?"], rules=[])
    assert result.overall == "needs_review"
    assert result.reason_code == ReasonCode.ENTITY_AMBIGUOUS


def test_pregnancy_context_rule_blocks():
    result = evaluate(
        ["ashwagandha"],
        [],
        {"pregnancy": True},
        rules=[rule("ashwagandha", severity="HIGH", evidence="PROBABLE", context_tag="pregnancy")],
    )
    assert result.overall == "block"


def test_context_rule_does_not_fire_without_flag():
    result = evaluate(
        ["ashwagandha"],
        [],
        {},
        rules=[rule("ashwagandha", severity="HIGH", evidence="PROBABLE", context_tag="pregnancy")],
    )
    assert result.overall == "pass"


def test_classical_evidence_never_blocks():
    result = evaluate(
        ["ashwagandha"],
        ["warfarin"],
        {},
        rules=[rule("ashwagandha", "warfarin", severity="SEVERE", evidence="CLASSICAL")],
    )
    assert result.overall == "caution"
    assert result.matches[0].reason_code == ReasonCode.CLASSICAL_CAUTION


def test_validated_high_severity_blocks():
    result = evaluate(
        ["ashwagandha"],
        ["warfarin"],
        {},
        rules=[rule("ashwagandha", "warfarin", severity="HIGH", evidence="VALIDATED")],
    )
    assert result.overall == "block"
    assert result.matches[0].reason_code == ReasonCode.INTERACTION_HIGH


def test_dose_below_threshold_skips_rule():
    result = evaluate(
        ["turmeric"],
        ["warfarin"],
        {},
        doses={"turmeric": "5 mg"},
        rules=[rule("turmeric", "warfarin", severity="HIGH", evidence="VALIDATED", dose_threshold="100 mg")],
    )
    assert result.overall == "needs_review"
    assert not result.matches


def test_polypharmacy_escalates_to_block():
    rules = [
        rule("herb_a", "drug_a", severity="MODERATE", evidence="PROBABLE"),
        rule("herb_b", "drug_b", severity="MODERATE", evidence="PROBABLE"),
    ]
    result = evaluate(["herb_a", "herb_b"], ["drug_a", "drug_b"], {}, rules=rules)
    assert result.overall == "block"
    assert result.reason_code == ReasonCode.POLYPHARMACY


def test_errors_fail_closed():
    result = fail_closed(RuntimeError("db exploded"))
    assert result.overall == "needs_review"
    assert result.reason_code == ReasonCode.ENGINE_ERROR
