"""Citation id mapping + source metadata packing for the UI.

Each source carries what the UI needs to show it in full: the corpus title, a link (the corpus
`source_url`, or a per-chapter link from `chapter_url_template` in data/raw/<source>/metadata.json),
the passage text the answer was grounded on, and any reference URLs inside that passage.
"""

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from urllib.parse import quote_plus

from app.config import get_settings

MAX_EXCERPT_CHARS = 4000
MAX_REFERENCES = 5
_SOURCE_NAME = re.compile(r"^[A-Za-z0-9_-]+$")
_URL = re.compile(r"https?://[^\s<>\"'\])]+")


@dataclass
class SourceRef:
    source: str
    chapter: str = ""
    verse: str = ""
    evidence_level: str = "classical"
    rights_url: str = ""
    title: str = ""
    url: str = ""
    license: str = ""
    excerpt: str = ""
    references: list[str] = field(default_factory=list)


@dataclass
class Citations:
    refs: list[SourceRef] = field(default_factory=list)

    def add(self, ref: SourceRef) -> str:
        self.refs.append(ref)
        return f"[S{len(self.refs)}]"

    def to_payload(self) -> list[dict]:
        return [{"id": f"S{i+1}", "source": r.source, "chapter": r.chapter, "verse": r.verse,
                 "evidence_level": r.evidence_level, "rights_url": r.rights_url, "title": r.title,
                 "url": r.url, "license": r.license, "excerpt": r.excerpt, "references": r.references}
                for i, r in enumerate(self.refs)]


@lru_cache(maxsize=64)
def corpus_info(source: str) -> dict:
    """data/raw/<source>/metadata.json, or {} when the corpus has none."""
    if not _SOURCE_NAME.match(source or ""):
        return {}
    path = get_settings().data_dir / "raw" / source / "metadata.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def source_ref(meta: dict, text: str) -> SourceRef:
    """A citation for one retrieved passage (chunk metadata + chunk text)."""
    source = meta.get("source", "unknown")
    chapter = meta.get("chapter", "")
    info = corpus_info(source)
    return SourceRef(
        source=source,
        chapter=chapter,
        verse=meta.get("verse", ""),
        evidence_level=meta.get("evidence_level", "classical"),
        title=info.get("title") or source.replace("_", " ").title(),
        url=_link(info, chapter),
        license=info.get("license", ""),
        excerpt=(text or "").strip()[:MAX_EXCERPT_CHARS],
        references=_references(text),
    )


def _link(info: dict, chapter: str) -> str:
    template = info.get("chapter_url_template")
    title = " ".join((chapter or "").split())
    if template and title and title.lower() != "introduction":
        return template.replace("{chapter}", quote_plus(title))
    return info.get("source_url") or ""


def _references(text: str) -> list[str]:
    found: list[str] = []
    for url in _URL.findall(text or ""):
        url = url.rstrip(".,;:")
        if url not in found:
            found.append(url)
    return found[:MAX_REFERENCES]
