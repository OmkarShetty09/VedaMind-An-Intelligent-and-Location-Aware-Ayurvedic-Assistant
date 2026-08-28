"""Singleton access to the configured vector store (pgvector default)."""

from app.config import get_settings

from .stores.base import VectorStore


def build_store() -> VectorStore:
    settings = get_settings()
    if settings.vector_store == "milvus":
        from .stores.milvus_store import MilvusStore

        return MilvusStore()
    from .stores.pgvector_store import PgVectorStore

    return PgVectorStore(settings.database_url, embedding_dim=settings.embedding_dim)


_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = build_store()
    return _store


def reset_store() -> None:
    """Reset the singleton store instance (for test isolation)."""
    global _store
    _store = None