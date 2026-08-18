from dataclasses import dataclass, field

from .alias_graph import ResolvedEntity, get_default_graph
from .constants import ALIAS_MATCH_THRESHOLD


@dataclass
class EntityExtraction:
    herbs: list[ResolvedEntity] = field(default_factory=list)
    drugs: list[ResolvedEntity] = field(default_factory=list)
    ambiguous: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.ambiguous


def extract_entities(text: str, graph=None) -> EntityExtraction:
    """Map free text to canonical herb/drug ids deterministically.

    Strategy: tokenize on alphanumeric runs; resolve each token via the alias
    graph. Tokens that fail resolution are classified as drugs only if they are
    neither known herbs nor filler words. Ambiguity (low confidence) is
    surfaced, never guessed.
    """
    graph = graph or get_default_graph()
    result = EntityExtraction()
    tokens = _tokenize(text)
    seen = set()
    for tok in tokens:
        key = tok.lower()
        if key in seen or key in _FILLER:
            continue
        seen.add(key)
        entity, conf = graph.resolve_ambiguous(tok)
        if entity is None:
            # not a known herb: treat as potential drug/substance if plausibly one
            if _looks_like_drug(tok):
                result.drugs.append(ResolvedEntity(tok, tok, 0.5, False))
            continue
        if conf < ALIAS_MATCH_THRESHOLD:
            result.ambiguous.append(tok)
            continue
        # a canonical herb name could also be the substance name of a drug
        if _is_drug_like(tok, graph):
            result.drugs.append(entity)
        else:
            result.herbs.append(entity)
    return result


def _tokenize(text: str) -> list[str]:
    import re

    return re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text)


def _looks_like_drug(tok: str) -> bool:
    return len(tok) >= 4


def _is_drug_like(tok: str, graph) -> bool:
    """Heuristic: a resolved herb token is drug-like if the raw token ends in -in,
    -ide, -ol, -ate, -zolam etc. (drug-suffix patterns). Deterministic only.
    """
    lowered = tok.lower()
    return lowered.endswith(("zolam", "pam", "-ide", "-ol", "-ate", "sartan", "statin", "mycin", "cillin"))


_FILLER = {
    "and", "the", "with", "for", "from", "take", "taking", "taken", "give", "dose", "dosage",
    "mg", "g", "gram", "grams", "tablet", "tablets", "capsule", "capsules", "tea", "spoon",
    "every", "daily", "once", "twice", "before", "after", "meal", "food", "herb", "herbs", "drug",
    "medicine", "medication", "please", "what", "can", "should", "i", "my", "me", "am", "is", "are",
}
