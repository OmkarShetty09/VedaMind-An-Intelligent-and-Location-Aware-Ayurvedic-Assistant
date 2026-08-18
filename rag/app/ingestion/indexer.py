"""End-to-end ingestion: raw -> chunks -> embeddings -> store + manifest."""

import json
import logging
from pathlib import Path

from app.config import get_settings
from app.retrieval.deps_store import get_store

from .chunker import chunk_document
from .embeddings import EmbeddingUnavailable, embed_texts
from .manifest import write_manifest
from .verifier import verify_source

logger = logging.getLogger("rag.ingestion.indexer")


def run_ingestion(raw_dir: Path, chunks_dir: Path, manifest_path: Path) -> int:
    """Verify -> load -> chunk -> embed -> upsert -> write manifest."""
    settings = get_settings()

    verified = [d for d in raw_dir.iterdir() if d.is_dir() and verify_source(d)[0]]
    if not verified:
        raise RuntimeError("No sources passed the rights gate; refusing to ingest.")

    from .loader import load_raw_sources

    docs = load_raw_sources(raw_dir)
    if not docs:
        raise RuntimeError("No documents loaded from corpus.")

    chunks = []
    for doc in docs:
        chunks.extend(chunk_document(doc, chunk_size=settings.chunk_size, overlap=settings.chunk_overlap))

    try:
        embeddings = embed_texts([c["content"] for c in chunks])
    except EmbeddingUnavailable:
        logger.error("Embedding unavailable; nothing written. Re-run with OPENAI_API_KEY.")
        raise

    chunks_dir.mkdir(parents=True, exist_ok=True)
    out_file = chunks_dir / "chunks.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    upserted = get_store().upsert(chunks, embeddings)
    write_manifest(manifest_path, version=settings.embedding_model, chunks=chunks,
                   embedding_model=settings.embedding_model, count=upserted)
    logger.info("Ingestion complete: %s chunks upserted", upserted)
    return upserted