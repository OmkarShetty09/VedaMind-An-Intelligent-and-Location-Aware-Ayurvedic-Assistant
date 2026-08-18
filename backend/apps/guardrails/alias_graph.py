import difflib
from dataclasses import dataclass
from functools import lru_cache

from .constants import ALIAS_MATCH_THRESHOLD, HERB_MIN_LENGTH
from .models import HerbAlias


@dataclass
class ResolvedEntity:
    canonical: str
    matched: str  # the alias/input that matched
    confidence: float
    is_exact: bool


def normalize(text: str) -> str:
    return " ".join("".join(c for c in text.lower() if c.isalnum() or c.isspace()).split())


class AliasGraph:
    """Deterministic name resolution. The LLM is never needed to name a herb."""

    def __init__(self, aliases: list[HerbAlias] | None = None):
        self._by_alias: dict[str, ResolvedEntity] = {}
        self._canonicals: set[str] = set()
        self._load(aliases or [])

    @staticmethod
    def build_from_db():
        return AliasGraph(list(HerbAlias.objects.all()))

    def _load(self, aliases):
        for row in aliases:
            key = normalize(row.alias)
            self._by_alias.setdefault(key, ResolvedEntity(row.canonical_herb, row.alias, row.confidence, True))
            self._canonicals.add(row.canonical_herb)
            self._by_alias.setdefault(
                normalize(row.canonical_herb),
                ResolvedEntity(row.canonical_herb, row.canonical_herb, 1.0, True),
            )
        for c in self._canonicals:
            self._by_alias.setdefault(normalize(c), ResolvedEntity(c, c, 1.0, True))

    def resolve(self, text: str) -> ResolvedEntity | None:
        key = normalize(text)
        if not key or len(key) < HERB_MIN_LENGTH:
            return None
        if key in self._by_alias:
            return self._by_alias[key]
        # fuzzy: best difflib match above threshold (handles typos/transliterations)
        best = difflib.get_close_matches(key, self._by_alias.keys(), n=1, cutoff=ALIAS_MATCH_THRESHOLD)
        if best:
            return ResolvedEntity(self._by_alias[best[0]].canonical, text, ALIAS_MATCH_THRESHOLD, False)
        return None

    def resolve_ambiguous(self, text: str) -> tuple[ResolvedEntity | None, float]:
        """Return (entity, confidence). Confidence < threshold signals ambiguity."""
        if not normalize(text):
            return None, 0.0
        # direct hit is exact; otherwise use fuzzy similarity score
        direct = self.resolve(text)
        if direct and direct.is_exact:
            return direct, 1.0
        if direct:
            sim = difflib.SequenceMatcher(None, normalize(text), normalize(direct.matched)).ratio()
            return direct, sim
        return None, 0.0

    @lru_cache(maxsize=512)  # noqa: B019 - graph is an immutable module-level singleton
    def resolve_cached(self, text: str) -> ResolvedEntity | None:
        return self.resolve(text)


_DEFAULT_GRAPH: AliasGraph | None = None


def get_default_graph() -> AliasGraph:
    global _DEFAULT_GRAPH
    if _DEFAULT_GRAPH is None:
        _DEFAULT_GRAPH = AliasGraph.build_from_db()
    return _DEFAULT_GRAPH


def reset_graph_cache():
    global _DEFAULT_GRAPH
    _DEFAULT_GRAPH = None
