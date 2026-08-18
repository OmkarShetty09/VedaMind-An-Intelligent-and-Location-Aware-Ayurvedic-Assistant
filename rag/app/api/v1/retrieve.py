from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings
from app.ingestion.embeddings import EmbeddingUnavailable, embed_query
from app.retrieval.deps_store import get_store
from app.retrieval.filters import apply_filters
from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import rerank

router = APIRouter()


class RetrieveRequest(BaseModel):
    query: str
    top_k: int | None = None
    context: dict = {}


@router.post("/retrieve")
def retrieve(payload: RetrieveRequest):
    """Debug/eval endpoint: return raw passages + scores."""
    settings = get_settings()
    filters = apply_filters(payload.query, payload.context)
    try:
        embedding = embed_query(payload.query)
        passages = hybrid_search(embedding, payload.query, filters)
    except EmbeddingUnavailable:
        passages = get_store().search_sparse(payload.query, settings.retrieval_candidates, filters)
    passages = rerank(passages, payload.query)[: payload.top_k or settings.retrieval_top_k]
    return {
        "passages": [
            {"id": p.chunk_id, "text": p.text[:500], "metadata": p.metadata, "score": round(p.score, 4)}
            for p in passages
        ]
    }