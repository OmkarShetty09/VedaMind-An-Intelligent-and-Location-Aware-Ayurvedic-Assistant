"""End-to-end ingestion: raw -> chunks -> embeddings -> store + manifest.

Idempotent: re-running ingestion replaces existing chunks (ON CONFLICT DO UPDATE).
Validates rights, metadata, source content, and embedding dimensions before inserting.
"""

import json
import logging
from pathlib import Path

from app.config import get_settings

from .chunker import chunk_document
from .embeddings import EmbeddingUnavailable, embed_texts
from .manifest import write_manifest
from .verifier import verify_source, verify_metadata, get_corpus_status

logger = logging.getLogger("rag.ingestion.indexer")


def scan_sources(raw_dir: Path) -> list[dict]:
    """Scan all source directories and report their status."""
    sources = []
    for source_dir in sorted(raw_dir.iterdir()):
        if not source_dir.is_dir():
            continue
        status = get_corpus_status(source_dir)
        rights_ok, rights_msg = verify_source(source_dir) if status != "NOT_AVAILABLE" else (False, "not checked")
        meta_ok, meta_msg = verify_metadata(source_dir) if status != "NOT_AVAILABLE" else (False, "not checked")
        source_md = source_dir / "source.md"
        sources.append({
            "name": source_dir.name,
            "status": status,
            "rights_ok": rights_ok,
            "rights_msg": rights_msg,
            "metadata_ok": meta_ok,
            "metadata_msg": meta_msg,
            "has_source_md": source_md.exists(),
            "source_md_size": source_md.stat().st_size if source_md.exists() else 0,
        })
    return sources


def run_ingestion(raw_dir: Path, chunks_dir: Path, manifest_path: Path, *, corpus_id: str | None = None) -> int:
    """Verify -> load -> chunk -> embed -> upsert -> write manifest.

    If corpus_id is provided, only ingest that specific corpus.
    """
    settings = get_settings()

    # 1. Scan and validate sources
    sources = scan_sources(raw_dir)
    verified = [s for s in sources if s["rights_ok"]]
    skipped = [s for s in sources if not s["rights_ok"] and s["status"] != "NOT_AVAILABLE"]

    for s in skipped:
        logger.warning("SKIPPED %s: %s", s["name"], s["rights_msg"])

    if not verified:
        raise RuntimeError(
            "No sources passed the rights gate; refusing to ingest. "
            f"Scanned {len(sources)} directories, {len(skipped)} skipped."
        )

    logger.info(
        "Sources: %d total, %d verified, %d skipped",
        len(sources), len(verified), len(skipped),
    )

    # 2. Load documents (verified only)
    from .loader import load_raw_sources

    docs = load_raw_sources(raw_dir, verified_only=True)
    if corpus_id:
        docs = [d for d in docs if d.get("corpus_id") == corpus_id]
    if not docs:
        raise RuntimeError("No documents loaded from corpus.")

    logger.info("Loaded %d chapter-level documents", len(docs))

    # 3. Chunk
    chunks = []
    for doc in docs:
        chunks.extend(chunk_document(doc, chunk_size=settings.chunk_size, overlap=settings.chunk_overlap))

    if not chunks:
        raise RuntimeError("Chunking produced zero chunks.")

    logger.info("Chunked into %d chunks", len(chunks))

    # 4. Validate chunks
    empty_chunks = [c for c in chunks if not c["content"].strip()]
    if empty_chunks:
        raise RuntimeError(f"{len(empty_chunks)} empty chunks detected; refusing to insert.")

    # 5. Embed
    try:
        embeddings = embed_texts([c["content"] for c in chunks])
    except EmbeddingUnavailable:
        logger.error("Embedding unavailable; nothing written. Re-run with OPENAI_API_KEY.")
        raise

    if len(embeddings) != len(chunks):
        raise RuntimeError(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks.")

    # 6. Upsert to vector store
    from app.retrieval.deps_store import get_store

    store = get_store()
    upserted = store.upsert(chunks, embeddings)

    # 7. Write chunks to disk (for inspection)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    out_file = chunks_dir / "chunks.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    # 8. Write manifest
    per_source = {}
    for c in chunks:
        src = c["metadata"].get("corpus_id", c["metadata"].get("source", "unknown"))
        per_source[src] = per_source.get(src, 0) + 1

    write_manifest(
        manifest_path,
        version=settings.embedding_model,
        chunks=chunks,
        embedding_model=settings.embedding_model,
        count=upserted,
        per_source=per_source,
    )

    logger.info("Ingestion complete: %s chunks upserted", upserted)
    return upserted


def corpus_status(raw_dir: Path, manifest_path: Path | None = None) -> dict:
    """Return full status report for all corpus sources."""
    sources = scan_sources(raw_dir)
    status = {
        "total_sources": len(sources),
        "verified": sum(1 for s in sources if s["rights_ok"]),
        "not_available": sum(1 for s in sources if s["status"] == "NOT_AVAILABLE"),
        "rights_unverified": sum(1 for s in sources if s["status"] == "RIGHTS_UNVERIFIED"),
        "ready": sum(1 for s in sources if s["status"] == "READY"),
        "failed": sum(1 for s in sources if s["status"] == "FAILED"),
        "sources": sources,
    }
    if manifest_path and manifest_path.exists():
        from .manifest import read_manifest
        status["manifest"] = read_manifest(manifest_path)
    return status
