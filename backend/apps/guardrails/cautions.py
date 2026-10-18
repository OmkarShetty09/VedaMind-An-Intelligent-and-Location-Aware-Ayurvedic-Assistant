"""'What not to take it with': the curated interaction rules for every herb a chat turn mentions.

Shown under every answer, whether or not the user has declared medication. The binding check
(rules_engine) only looks at the user's own medicines; this lists everything the ruleset knows
about the herbs in the question and the answer, with modern-medicine examples for each drug
class, so the user can see what to keep apart. Deterministic: exact alias matches only (fuzzy
matching on answer prose would flag ordinary words as herbs).
"""

from .alias_graph import get_default_graph
from .drug_lexicon import get_default_lexicon
from .entity_extraction import _tokenize, extract_entities
from .models import InteractionRule
from .severity import Severity

GENERAL_NOTE = (
    "Taking any modern (allopathic) medicine - for example for blood pressure, diabetes, thyroid, blood "
    "thinning, sleep, mood or pain? Tell your doctor or pharmacist before combining it with any Ayurvedic "
    "herb or formulation, including ones not listed here, and never stop or change a prescribed medicine "
    "on your own."
)
NO_RULES_NOTE = (
    "VedaMind's curated interaction list has no entry for {herbs}. That is not proof it is safe with "
    "your medicines - check with your doctor or pharmacist."
)

_CONTEXT_LABELS = {
    "pregnancy": "Pregnancy or breastfeeding",
    "pediatric": "Children under 12",
    "renal": "Kidney problems",
    "diabetes": "Diabetes",
}
_NAME_FIXES = {"nsaids": "NSAIDs", "ace inhibitors": "ACE inhibitors"}
_MAX_EXAMPLES = 3


def herbs_mentioned(text: str, graph=None) -> list[str]:
    """Canonical herbs named in `text` (exact alias hits on 1-3 word windows), in order of mention."""
    graph = graph or get_default_graph()
    tokens = _tokenize(text or "")
    found: list[str] = []
    consumed: set[int] = set()
    for size in (3, 2, 1):
        for start in range(len(tokens) - size + 1):
            if any(i in consumed for i in range(start, start + size)):
                continue
            entity = graph.resolve_exact(" ".join(tokens[start : start + size]))
            if entity is not None:
                consumed.update(range(start, start + size))
                if entity.canonical not in found:
                    found.append(entity.canonical)
    return found


def cautions_for(text: str, medications: list[str] | None = None) -> dict:
    """{herbs, items: [...], general, note} for the herbs in `text`.

    items: {herb, avoid_with, examples, kind: medicine|herb|condition, severity, evidence,
            recommendation, mechanism, source_uri, applies_to_you}
    """
    herbs = herbs_mentioned(text)
    lexicon = get_default_lexicon()
    class_members: dict[str, list[str]] = {}
    for drug, classes in lexicon.class_map().items():
        for cls in classes:
            class_members.setdefault(cls, []).append(drug)
    user_drugs = _user_drug_names(medications or [], lexicon)

    items = []
    rules = InteractionRule.objects.filter(active=True, herb_a__in=herbs) if herbs else []
    for rule in rules:
        target = (rule.herb_b_or_drug or "").strip().lower()
        if target:
            kind = "herb" if rule.direction == "herb_herb" else "medicine"
            avoid_with = _humanize(target)
            examples = [] if kind == "herb" else sorted(d for d in class_members.get(target, []) if d != target)
        else:
            kind = "condition"
            avoid_with = _CONTEXT_LABELS.get(rule.context_tag, _humanize(rule.context_tag or "some conditions"))
            examples = []
        items.append(
            {
                "herb": rule.herb_a,
                "avoid_with": avoid_with,
                "examples": [_humanize(e) for e in examples[:_MAX_EXAMPLES]],
                "kind": kind,
                "severity": rule.severity.lower(),
                "evidence": rule.evidence.lower(),
                "recommendation": rule.recommendation,
                "mechanism": rule.mechanism,
                "source_uri": rule.source_uri,
                "applies_to_you": bool(target) and (target in user_drugs),
            }
        )
    items.sort(key=lambda i: (herbs.index(i["herb"]), not i["applies_to_you"], -_severity_rank(i["severity"])))

    covered = {i["herb"] for i in items}
    uncovered = [h for h in herbs if h not in covered]
    return {
        "herbs": herbs,
        "items": items,
        "general": GENERAL_NOTE,
        "note": NO_RULES_NOTE.format(herbs=_join(uncovered)) if uncovered else "",
    }


def _user_drug_names(medications: list[str], lexicon) -> set[str]:
    """The user's declared medicines plus the drug classes they belong to."""
    names: set[str] = set()
    for drug in extract_entities("", get_default_graph(), medications=medications, lexicon=lexicon).drugs:
        names.add(drug.canonical)
        names.update(lexicon.classes_for(drug.canonical))
    return names


def _severity_rank(name: str) -> int:
    return Severity[name.upper()].value if name.upper() in Severity.__members__ else 0


def _humanize(name: str) -> str:
    text = name.replace("_", " ").strip()
    return _NAME_FIXES.get(text.lower(), text[:1].upper() + text[1:])


def _join(names: list[str]) -> str:
    names = [n.title() for n in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " or " + names[-1]
