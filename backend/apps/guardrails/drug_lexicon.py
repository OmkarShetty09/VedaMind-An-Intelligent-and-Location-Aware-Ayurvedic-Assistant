"""Drug name resolution backed by the DrugAlias table (cached like the herb AliasGraph)."""

from .alias_graph import normalize
from .models import DrugAlias


class DrugLexicon:
    def __init__(self, rows: list[DrugAlias] | None = None):
        self._canonical: dict[str, str] = {}
        self._classes: dict[str, set[str]] = {}
        for row in rows or []:
            alias, canonical = normalize(row.alias), normalize(row.canonical)
            self._canonical[alias] = canonical
            self._classes.setdefault(canonical, set()).update(c.lower() for c in (row.classes or []))

    @staticmethod
    def build_from_db() -> "DrugLexicon":
        return DrugLexicon(list(DrugAlias.objects.all()))

    def resolve(self, token: str) -> str | None:
        """Canonical drug/class name for a token, or None if it is not a known drug."""
        return self._canonical.get(normalize(token))

    def classes_for(self, drug: str) -> set[str]:
        return set(self._classes.get(normalize(drug), set()))

    def class_map(self) -> dict[str, set[str]]:
        return {drug: set(classes) for drug, classes in self._classes.items()}

    def __bool__(self) -> bool:
        return bool(self._canonical)


_DEFAULT: DrugLexicon | None = None


def get_default_lexicon() -> DrugLexicon:
    global _DEFAULT
    if not _DEFAULT:  # also rebuild when empty (built before seed_demo_data ran)
        _DEFAULT = DrugLexicon.build_from_db()
    return _DEFAULT


def reset_lexicon_cache() -> None:
    global _DEFAULT
    _DEFAULT = None
