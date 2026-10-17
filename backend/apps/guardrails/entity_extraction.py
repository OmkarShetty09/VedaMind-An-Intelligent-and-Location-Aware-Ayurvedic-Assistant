import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .alias_graph import ResolvedEntity, get_default_graph
from .constants import ALIAS_MATCH_THRESHOLD
from .drug_lexicon import DrugLexicon, get_default_lexicon

_TEXT_RULES_PATH = Path(__file__).resolve().parent / "data" / "text_rules.json"


@lru_cache(maxsize=1)
def text_rules() -> dict:
    """Tokenisation rules (filler words, drug-name stems, dose words) from data/text_rules.json."""
    rules = json.loads(_TEXT_RULES_PATH.read_text(encoding="utf-8"))
    return {
        "filler": frozenset(rules["filler_words"]),
        "dose_words": frozenset(rules["dose_words"]),
        "stems": tuple(rules["drug_stems"]),
        "stem_min_length": int(rules["drug_stem_min_length"]),
        "not_drugs": frozenset(rules["not_drugs"]),
    }


@dataclass
class EntityExtraction:
    herbs: list[ResolvedEntity] = field(default_factory=list)
    drugs: list[ResolvedEntity] = field(default_factory=list)
    ambiguous: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.ambiguous


def extract_entities(
    text: str, graph=None, medications: list[str] | None = None, lexicon: DrugLexicon | None = None
) -> EntityExtraction:
    """Map free text (+ the user's declared medications) to canonical herb/drug ids deterministically.

    Strategy: tokenize on alphanumeric runs; multi-word herb aliases ("winter cherry") are matched
    first, then each token is resolved as a known drug (DrugAlias table), a herb (HerbAlias graph),
    or a drug by its INN stem. Ordinary words are ignored - only recognisable drugs count as drugs,
    otherwise every question mentioning a herb ("turmeric for joint pain") would look like a novel
    pair. Every entry in `medications` is a drug by declaration, recognised or not. Ambiguity (low
    confidence) is surfaced, never guessed.
    """
    graph = graph or get_default_graph()
    lexicon = lexicon if lexicon is not None else get_default_lexicon()
    rules = text_rules()
    result = EntityExtraction()
    seen_herbs: set[str] = set()
    seen_drugs: set[str] = set()

    def add_herb(entity: ResolvedEntity):
        if entity.canonical not in seen_herbs:
            seen_herbs.add(entity.canonical)
            result.herbs.append(entity)

    def add_drug(name: str, matched: str, confidence: float, exact: bool):
        if name not in seen_drugs:
            seen_drugs.add(name)
            result.drugs.append(ResolvedEntity(name, matched, confidence, exact))

    tokens = _tokenize(text)
    consumed: set[int] = set()
    for size in (3, 2):
        for start in range(len(tokens) - size + 1):
            if any(i in consumed for i in range(start, start + size)):
                continue
            phrase = " ".join(tokens[start : start + size])
            entity = graph.resolve_exact(phrase)
            if entity is not None:
                add_herb(entity)
                consumed.update(range(start, start + size))

    seen_tokens: set[str] = set()
    for i, tok in enumerate(tokens):
        key = tok.lower()
        if i in consumed or key in seen_tokens or key in rules["filler"]:
            continue
        seen_tokens.add(key)
        drug = lexicon.resolve(key)
        if drug:
            add_drug(drug, tok, 1.0, True)
            continue
        entity, conf = graph.resolve_ambiguous(tok)
        if entity is None:
            if looks_like_drug(key):
                add_drug(key, tok, 0.5, False)
            continue
        if conf < ALIAS_MATCH_THRESHOLD:
            result.ambiguous.append(tok)
            continue
        # a canonical herb name could also be the substance name of a drug
        if _is_drug_like(tok):
            add_drug(entity.canonical, tok, entity.confidence, entity.is_exact)
        else:
            add_herb(entity)

    skip = rules["filler"] | rules["dose_words"]
    for med in medications or []:
        med_tokens = [t.lower() for t in _tokenize(str(med)) if t.lower() not in skip]
        if not med_tokens:
            continue
        known = [d for d in (lexicon.resolve(t) or (t if looks_like_drug(t) else None) for t in med_tokens) if d]
        if known:
            for name in known:
                add_drug(name, str(med), 1.0, True)
        else:
            # Declared by the user but not in our vocabulary: still a drug (fails safe as a novel pair).
            add_drug(" ".join(med_tokens), str(med), 0.5, False)
    return result


def looks_like_drug(key: str) -> bool:
    rules = text_rules()
    return len(key) >= rules["stem_min_length"] and key not in rules["not_drugs"] and key.endswith(rules["stems"])


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text)


def _is_drug_like(tok: str) -> bool:
    """Heuristic: a resolved herb token is drug-like if the raw token ends in -in,
    -ide, -ol, -ate, -zolam etc. (drug-suffix patterns). Deterministic only.
    """
    lowered = tok.lower()
    return lowered.endswith(("zolam", "pam", "-ide", "-ol", "-ate", "sartan", "statin", "mycin", "cillin"))
