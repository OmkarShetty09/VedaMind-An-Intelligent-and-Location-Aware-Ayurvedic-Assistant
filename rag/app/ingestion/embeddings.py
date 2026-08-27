"""Embedding generation + query embedding. Model version is pinned for reproducibility."""

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger("rag.ingestion.embeddings")

_URL = "https://api.openai.com/v1/embeddings"


class EmbeddingUnavailable(Exception):
    pass


class EmbeddingDimensionError(Exception):
    pass


def _headers():
    key = get_settings().openai_api_key
    if not key:
        raise EmbeddingUnavailable("OPENAI_API_KEY not configured")
    return {"Authorization": f"Bearer {key}"}


def _validate_dimensions(embeddings: list[list[float]], expected_dim: int, batch_start: int):
    for i, emb in enumerate(embeddings):
        if len(emb) != expected_dim:
            raise EmbeddingDimensionError(
                f"Embedding at index {batch_start + i} has {len(emb)} dimensions, expected {expected_dim}"
            )


def embed_texts(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    out: list[list[float]] = []
    batch = 100
    for start in range(0, len(texts), batch):
        chunk = texts[start : start + batch]
        if not any(t.strip() for t in chunk):
            raise EmbeddingUnavailable("All texts in batch are empty")
        for attempt in range(3):
            try:
                resp = httpx.post(
                    _URL,
                    json={"model": settings.embedding_model, "input": chunk, "dimensions": settings.embedding_dim},
                    headers=_headers(),
                    timeout=120.0,
                )
                resp.raise_for_status()
                data = resp.json()["data"]
                batch_embeddings = [item["embedding"] for item in sorted(data, key=lambda d: d["index"])]
                _validate_dimensions(batch_embeddings, settings.embedding_dim, start)
                out.extend(batch_embeddings)
                break
            except httpx.HTTPError as exc:
                if attempt == 2:
                    raise EmbeddingUnavailable(f"embedding failed after 3 attempts: {exc}") from exc
                logger.warning("Embedding retry %s/3: %s", attempt + 1, exc)
    return out


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
