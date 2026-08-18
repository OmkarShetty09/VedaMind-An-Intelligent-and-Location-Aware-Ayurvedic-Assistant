"""Hybrid retrieval: RRF fusion of dense (pgvector) + sparse (tsvector)."""

import logging

from app.config import get_settings

from .deps_store import get_store
from .stores.base import Passage

logger = logging.getLogger("rag.retrieval.hybrid")

RRF_K = 60
DENSE_WEIGHT = 0.6
SPARSE_WEIGHT = 0.4


def hybrid_search(query_embedding: list[float], query_text: str, filters: dict | None = None) -> list[Passage]:
    settings = get_settings()
    store = get_store()
    k = settings.retrieval_candidates

    dense = store.search_dense(query_embedding, k, filters)
    sparse = store.search_sparse(query_text, k, filters)

    scores: dict[str, dict] = {}
    for rank, p in enumerate(dense, start=1):
        entry = scores.setdefault(p.chunk_id, {"passage": p, "rrf": 0.0})
        entry["rrf"] += DENSE_WEIGHT * (1.0 / (RRF_K + rank))

    for rank, p in enumerate(sparse, start=1):
        entry = scores.setdefault(p.chunk_id, {"passage": p, "rrf": 0.0})
        entry["rrf"] += SPARSE_WEIGHT * (1.0 / (RRF_K + rank))

    fused = sorted(scores.values(), key=lambda e: e["rrf"], reverse=True)
    for e in fused:
        e["passage"].score = e["rrf"]
    logger.info("hybrid: dense=%s sparse=%s fused=%s", len(dense), len(sparse), len(fused))
    return [e["passage"] for e in fused]