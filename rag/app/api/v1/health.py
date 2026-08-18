from fastapi import APIRouter, Request

from app.config import get_settings

router = APIRouter()


@router.get("/health")
def health(request: Request):
    settings = get_settings()
    store_ok = True
    try:
        from app.retrieval.deps_store import get_store

        get_store()
    except Exception:  # noqa: BLE001 - health probe must never raise
        store_ok = False
    return {"status": "ok" if store_ok else "degraded", "store": settings.vector_store,
            "correlation_id": request.state.correlation_id}