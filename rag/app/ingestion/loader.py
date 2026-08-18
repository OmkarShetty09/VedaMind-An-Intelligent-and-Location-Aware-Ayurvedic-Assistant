"""Raw corpus loading: data/raw/<source>/source.md -> normalized documents."""

from pathlib import Path


def load_raw_sources(raw_dir: Path) -> list[dict]:
    """Load each source.md, splitting on '# ' headings into chapters."""
    docs: list[dict] = []
    for source_dir in sorted(raw_dir.iterdir()):
        if not source_dir.is_dir():
            continue
        source_md = source_dir / "source.md"
        if not source_md.exists():
            continue
        source_name = source_dir.name
        content = source_md.read_text(encoding="utf-8")
        chapters = _split_chapters(source_name, content)
        docs.extend(chapters)
    return docs


def _split_chapters(source: str, content: str) -> list[dict]:
    lines = content.splitlines()
    chapters: list[dict] = []
    current_title = "introduction"
    current = []
    for line in lines:
        if line.startswith("# "):
            if current:
                chapters.append({"id": f"{source}:{_slug(current_title)}", "source": source,
                                 "chapter": current_title, "content": "\n".join(current)})
            current_title = line[2:].strip()
            current = []
        else:
            current.append(line)
    if current:
        chapters.append({"id": f"{source}:{_slug(current_title)}", "source": source,
                         "chapter": current_title, "content": "\n".join(current)})
    return chapters


def _slug(title: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")