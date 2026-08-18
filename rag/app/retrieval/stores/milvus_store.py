import logging

from .base import Passage, VectorStore

logger = logging.getLogger("rag.retrieval.milvus")


class MilvusStore(VectorStore):
    """v2 adapter for Milvus (native hybrid dense+sparse). Not wired in v1.

    Kept behind the same interface so the swap is a config flag (VECTOR_STORE).
    """

    def __init__(self, uri: str = "http://milvus:19530"):
        self._uri = uri
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            try:
                from pymilvus import MilvusClient  # optional dependency

                self._client = MilvusClient(uri=self._uri)
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError("pymilvus not installed; VECTOR_STORE=milvus requires it.") from exc
        return self._client

    def search_dense(self, embedding, top_k, filters=None) -> list[Passage]:
        client = self._ensure_client()
        hits = client.search("rag_chunks", data=[embedding], limit=top_k,
                             filter=_milvus_filter(filters), output_fields=["content", "metadata"])
        out = []
        for h in hits[0]:
            out.append(Passage(chunk_id=h["id"], text=h["entity"]["content"],
                               metadata=h["entity"].get("metadata", {}), score=h["distance"]))
        return out

    def search_sparse(self, query, top_k, filters=None) -> list[Passage]:
        # Milvus hybrid needs a sparse index; abstracted here, returns empty in v1.
        logger.warning("Milvus sparse search requires sparse index config; returning []")
        return []

    def upsert(self, chunks, embeddings) -> int:
        client = self._ensure_client()
        data = [
            {"id": c["id"], "content": c["content"], "metadata": c["metadata"], "vector": emb}
            for c, emb in zip(chunks, embeddings)
        ]
        client.insert("rag_chunks", data)
        return len(data)


def _milvus_filter(filters: dict | None) -> str:
    if not filters:
        return ""
    parts = []
    if filters.get("source"):
        parts.append(f'metadata["source"] == "{filters["source"]}"')
    if filters.get("evidence_level"):
        parts.append(f'metadata["evidence_level"] == "{filters["evidence_level"]}"')
    return " and ".join(parts)