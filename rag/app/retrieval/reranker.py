import logging

from app.config import get_settings

from .stores.base import Passage

logger = logging.getLogger("rag.retrieval.rerank")

MIN_RELEVANCE_SCORE = 0.2  # below this, treat as unsupported -> refusal


def rerank(passages: list[Passage], query: str) -> list[Passage]:
    settings = get_settings()
    if not settings.reranker_enabled:
        return passages[: settings.retrieval_top_k]

    try:

        model = _get_model(settings.reranker_model)
        pairs = [(query, p.text) for p in passages[:50]]
        scores = model.predict(pairs)
        ranked = sorted(zip(passages[:50], scores), key=lambda t: t[1], reverse=True)
        out = []
        for p, score in ranked[: settings.retrieval_top_k]:
            p.score = float(score)
            out.append(p)
        return out
    except Exception as exc:  # noqa: BLE001 - model unavailable -> degrade to fused order
        logger.warning("Reranker unavailable (%s); using fused order.", exc)
        return passages[: settings.retrieval_top_k]


_model = None


def _get_model(name: str):
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder

        _model = CrossEncoder(name)
    return _model