from fastapi import APIRouter, Request

from app.config import get_settings

router = APIRouter()


@router.get("/health")
def health(request: Request):
    settings = get_settings()
    store_ok = True
    chunk_count = 0
    chunks_by_source = []
    try:
        from app.retrieval.deps_store import get_store
        store = get_store()
        chunk_count = store.count_chunks()
        chunks_by_source = store.count_by_source()
    except Exception:  # noqa: BLE001 - health probe must never raise
        store_ok = False

    kb_status = "EMPTY" if chunk_count == 0 else "POPULATED"

    return {
        "status": "ok" if store_ok else "degraded",
        "store": settings.vector_store,
        "rag_chunks": chunk_count,
        "chunks_by_source": [{"source": s, "count": c} for s, c in chunks_by_source],
        "knowledge_base": kb_status,
        "embedding_model": settings.embedding_model,
        "embedding_dim": settings.embedding_dim,
        "correlation_id": request.state.correlation_id,
    }
