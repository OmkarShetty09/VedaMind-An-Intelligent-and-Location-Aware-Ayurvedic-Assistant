from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Passage:
    chunk_id: str
    text: str
    metadata: dict
    score: float


class VectorStore(ABC):
    """Storage contract. pgvector is the v1 default; Milvus is the v2 adapter."""

    @abstractmethod
    def search_dense(self, embedding: list[float], top_k: int, filters: dict | None = None) -> list[Passage]:
        ...

    @abstractmethod
    def search_sparse(self, query: str, top_k: int, filters: dict | None = None) -> list[Passage]:
        ...

    @abstractmethod
    def upsert(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        ...

    def close(self):
        return None