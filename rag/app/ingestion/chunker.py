"""Shloka-aware chunker: never splits a verse; prose uses overlapping windows.

Chunk unit = 1-3 consecutive verses (shlokas) plus attached commentary lines.
Prose sections (commentaries) are split on a token window with overlap so no
content is lost, but verse lines always stay whole.
"""

import re
from collections.abc import Iterable

_VERSE_LINE = re.compile(r"^\s*[\d\u0966-\u096F]+[.)]\s", re.MULTILINE)


def _split_blocks(content: str) -> Iterable[str]:
    """Yield (verse | prose) atomic blocks."""
    lines = content.splitlines()
    current_verse: list[str] = []
    current_prose: list[str] = []

    for line in lines:
        if _VERSE_LINE.match(line):
            if current_prose:
                yield "\n".join(current_prose)
                current_prose = []
            current_verse.append(line)
        else:
            if current_verse:
                yield "\n".join(current_verse)
                current_verse = []
            current_prose.append(line)
    if current_verse:
        yield "\n".join(current_verse)
    if current_prose:
        yield "\n".join(current_prose)


def _prose_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    out = []
    start = 0
    while start < len(words):
        out.append(" ".join(words[start : start + chunk_size]))
        start += chunk_size - overlap
    return out


def chunk_document(doc: dict, *, chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """doc: {id, source, chapter, content, evidence_level, verse_range_hint, corpus_id, source_type}"""
    blocks = list(_split_blocks(doc["content"]))
    chunks: list[dict] = []
    group: list[str] = []
    group_tokens = 0
    verse_no = 0
    chunk_index = 0

    def emit(blocks_to_group: list[str], kind: str):
        nonlocal verse_no, chunk_index
        text = "\n".join(blocks_to_group)
        chunk_id = f"{doc['id']}:c{chunk_index}"
        chunks.append(
            {
                "id": chunk_id,
                "content": text,
                "metadata": {
                    "source": doc["source"],
                    "chapter": doc.get("chapter", ""),
                    "verse": _verse_label(doc, verse_no),
                    "evidence_level": doc.get("evidence_level", "classical"),
                    "corpus_id": doc.get("corpus_id", doc["source"]),
                    "source_type": doc.get("source_type", "GENERAL"),
                    "chunk_index": chunk_index,
                },
            }
        )
        verse_no += 1
        chunk_index += 1

    for block in blocks:
        n = max(1, len(block.split()))
        is_verse = bool(_VERSE_LINE.match(block or "\n"))
        if is_verse:
            # verse cluster: 1-3 verses per chunk, no overlap (avoids dup citations)
            if group_tokens + n > chunk_size and group:
                emit(group, "verse")
                group = []
                group_tokens = 0
            group.append(block)
            group_tokens += n
        else:
            if group:
                emit(group, "verse")
                group = []
                group_tokens = 0
            for pc in _prose_chunks(block, chunk_size, overlap):
                chunk_id = f"{doc['id']}:c{chunk_index}"
                chunks.append(
                    {
                        "id": chunk_id,
                        "content": pc,
                        "metadata": {
                            "source": doc["source"],
                            "chapter": doc.get("chapter", ""),
                            "verse": doc.get("verse_range_hint", ""),
                            "evidence_level": doc.get("evidence_level", "classical"),
                            "corpus_id": doc.get("corpus_id", doc["source"]),
                            "source_type": doc.get("source_type", "GENERAL"),
                            "chunk_index": chunk_index,
                        },
                    }
                )
                chunk_index += 1
    if group:
        emit(group, "verse")
    return chunks


def _verse_label(doc: dict, verse_no: int) -> str:
    if doc.get("verse_range_hint"):
        return doc["verse_range_hint"]
    return f"vv. {verse_no + 1}"
