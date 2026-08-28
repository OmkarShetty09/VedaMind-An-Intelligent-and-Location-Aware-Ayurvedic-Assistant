"""Embedding generation + query embedding. Supports OpenAI and Gemini providers."""

import logging
import time

import httpx

from app.config import get_settings

logger = logging.getLogger("rag.ingestion.embeddings")

_OPENAI_URL = "https://api.openai.com/v1/embeddings"
_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class EmbeddingUnavailable(Exception):
    pass


class EmbeddingDimensionError(Exception):
    pass


def _validate_dimensions(embeddings: list[list[float]], expected_dim: int, batch_start: int):
    for i, emb in enumerate(embeddings):
        if len(emb) != expected_dim:
            raise EmbeddingDimensionError(
                f"Embedding at index {batch_start + i} has {len(emb)} dimensions, expected {expected_dim}"
            )


def _embed_openai(texts: list[str], model: str, dim: int) -> list[list[float]]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise EmbeddingUnavailable("OPENAI_API_KEY not configured")
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    out: list[list[float]] = []
    batch = 100
    for start in range(0, len(texts), batch):
        chunk = texts[start : start + batch]
        for attempt in range(3):
            try:
                resp = httpx.post(
                    _OPENAI_URL,
                    json={"model": model, "input": chunk, "dimensions": dim},
                    headers=headers,
                    timeout=120.0,
                )
                resp.raise_for_status()
                data = resp.json()["data"]
                batch_embeddings = [item["embedding"] for item in sorted(data, key=lambda d: d["index"])]
                _validate_dimensions(batch_embeddings, dim, start)
                out.extend(batch_embeddings)
                break
            except httpx.HTTPError as exc:
                if attempt == 2:
                    raise EmbeddingUnavailable(f"embedding failed after 3 attempts: {exc}") from exc
                logger.warning("Embedding retry %s/3: %s", attempt + 1, exc)
    return out


def _embed_gemini(texts: list[str], model: str, dim: int) -> list[list[float]]:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise EmbeddingUnavailable("GEMINI_API_KEY not configured")

    out: list[list[float]] = []
    batch = 10
    for start in range(0, len(texts), batch):
        chunk = texts[start : start + batch]
        success = False
        for attempt in range(5):
            try:
                resp = httpx.post(
                    f"{_GEMINI_URL}/{model}:batchEmbedContents",
                    json={
                        "requests": [
                            {"model": f"models/{model}", "content": {"parts": [{"text": t}]}, "outputDimensionality": dim}
                            for t in chunk
                        ]
                    },
                    headers={"x-goog-api-key": settings.gemini_api_key},
                    timeout=120.0,
                )
                if resp.status_code == 429:
                    wait = min(2 ** attempt * 5, 60)
                    logger.warning("Gemini rate limited, waiting %ss (attempt %s/5)", wait, attempt + 1)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                batch_embeddings = [item["values"] for item in resp.json()["embeddings"]]
                _validate_dimensions(batch_embeddings, dim, start)
                out.extend(batch_embeddings)
                success = True
                break
            except httpx.HTTPError as exc:
                if attempt == 4:
                    raise EmbeddingUnavailable(f"embedding failed after 5 attempts: {exc}") from exc
                logger.warning("Embedding retry %s/5: %s", attempt + 1, exc)
                time.sleep(2 ** attempt)
        if not success:
            raise EmbeddingUnavailable(f"embedding batch starting at {start} failed after 5 attempts (rate limited)")
        if start + batch < len(texts):
            time.sleep(2)
    return out


def _is_valid_key(key: str) -> bool:
    return bool(key) and not key.endswith("...") and len(key) > 10


def embed_texts(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    if not any(t.strip() for t in texts):
        raise EmbeddingUnavailable("All texts are empty")

    if _is_valid_key(settings.gemini_api_key):
        gemini_model = "gemini-embedding-001"
        return _embed_gemini(texts, gemini_model, settings.embedding_dim)
    if _is_valid_key(settings.openai_api_key):
        return _embed_openai(texts, settings.embedding_model, settings.embedding_dim)
    raise EmbeddingUnavailable("No valid embedding API key configured (set GEMINI_API_KEY or OPENAI_API_KEY)")


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
