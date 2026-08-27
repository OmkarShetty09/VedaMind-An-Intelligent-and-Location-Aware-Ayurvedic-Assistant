"""Build rich metadata for each chunk, including provenance fields."""

import hashlib


def build_chunk_metadata(
    *,
    source: str,
    chapter: str = "",
    verse: str = "",
    evidence_level: str = "classical",
    corpus_id: str | None = None,
    source_type: str | None = None,
    chunk_index: int = 0,
    rights_status: str | None = None,
) -> dict:
    """Construct the metadata dict stored alongside each chunk."""
    return {
        "source": source,
        "chapter": chapter,
        "verse": verse,
        "evidence_level": evidence_level,
        "corpus_id": corpus_id or source,
        "source_type": source_type or "GENERAL",
        "chunk_index": chunk_index,
        "rights_status": rights_status or "UNKNOWN",
    }


def content_hash(text: str) -> str:
    """SHA-256 hash of chunk content for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()
