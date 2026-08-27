"""Raw corpus loading: data/raw/<source>/source.md -> normalized documents.

Loads metadata.json alongside source.md to enrich each document with
corpus-level provenance information.
"""

import json
from pathlib import Path


def load_raw_sources(raw_dir: Path, verified_only: bool = True) -> list[dict]:
    """Load each source.md, splitting on '# ' headings into chapters.

    If verified_only=True, skips sources that don't pass verify_source().
    """
    from .verifier import verify_source

    docs: list[dict] = []
    for source_dir in sorted(raw_dir.iterdir()):
        if not source_dir.is_dir():
            continue
        source_md = source_dir / "source.md"
        if not source_md.exists():
            continue
        if source_md.stat().st_size == 0:
            continue
        if verified_only:
            ok, reason = verify_source(source_dir)
            if not ok:
                continue
        source_name = source_dir.name
        content = source_md.read_text(encoding="utf-8")
        if not content.strip():
            continue
        meta = _load_metadata(source_dir)
        chapters = _split_chapters(source_name, content, meta)
        docs.extend(chapters)
    return docs


def _load_metadata(source_dir: Path) -> dict:
    meta_path = source_dir / "metadata.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _split_chapters(source: str, content: str, meta: dict | None = None) -> list[dict]:
    meta = meta or {}
    lines = content.splitlines()
    chapters: list[dict] = []
    current_title = "introduction"
    current = []
    for line in lines:
        if line.startswith("# "):
            if current:
                chapters.append(_make_doc(source, current_title, "\n".join(current), meta))
            current_title = line[2:].strip()
            current = []
        else:
            current.append(line)
    if current:
        chapters.append(_make_doc(source, current_title, "\n".join(current), meta))
    return chapters


def _make_doc(source: str, chapter: str, content: str, meta: dict) -> dict:
    return {
        "id": f"{source}:{_slug(chapter)}",
        "source": source,
        "chapter": chapter,
        "content": content,
        "corpus_id": meta.get("corpus_id", source),
        "source_type": meta.get("source_type", "GENERAL"),
    }


def _slug(title: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
