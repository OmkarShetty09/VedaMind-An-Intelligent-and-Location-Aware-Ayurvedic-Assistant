"""Context window assembly: relevance-ordered passages, capped by token budget."""

from app.config import get_settings
from app.llm.token_budget import enforce_context_budget

from .citations import Citations, SourceRef
from .errors import RetrievalError


def assemble(passages: list, citations: Citations) -> list[dict]:
    """Pack retrieved passages into template-ready items + populate citations.

    Drops lowest-ranked passages first (never mid-shloka: chunks are atomic).
    """
    settings = get_settings()
    items = []
    for p in passages:
        ref = SourceRef(
            source=p.metadata.get("source", "unknown"),
            chapter=p.metadata.get("chapter", ""),
            verse=p.metadata.get("verse", ""),
            evidence_level=p.metadata.get("evidence_level", "classical"),
        )
        citations.add(ref)
        items.append({"chunk_id": p.chunk_id, "content": p.text, "metadata": p.metadata})
    kept = enforce_context_budget(items, settings.context_max_tokens)
    if not kept:
        raise RetrievalError("No context fits the budget.")
    return kept