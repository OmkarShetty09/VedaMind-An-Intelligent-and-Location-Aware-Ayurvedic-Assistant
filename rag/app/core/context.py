"""Context window assembly: relevance-ordered passages, capped by token budget."""

from app.config import get_settings
from app.llm.token_budget import enforce_context_budget

from .citations import Citations, SourceRef
from .errors import RetrievalError


def assemble(passages: list, citations: Citations) -> list[dict]:
    """Pack retrieved passages into template-ready items + populate citations.

    Drops lowest-ranked passages first (never mid-shloka: chunks are atomic). Citations are
    numbered over the kept passages only, so [S1]..[Sn] in the prompt and in the UI agree.
    """
    settings = get_settings()
    items = [{"chunk_id": p.chunk_id, "content": p.text, "metadata": p.metadata} for p in passages]
    kept = enforce_context_budget(items, settings.context_max_tokens)
    if not kept:
        raise RetrievalError("No context fits the budget.")
    for item in kept:
        meta = item["metadata"]
        citations.add(
            SourceRef(
                source=meta.get("source", "unknown"),
                chapter=meta.get("chapter", ""),
                verse=meta.get("verse", ""),
                evidence_level=meta.get("evidence_level", "classical"),
            )
        )
    return kept
