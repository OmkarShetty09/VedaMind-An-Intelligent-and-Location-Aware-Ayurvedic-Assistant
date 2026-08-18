"""Citation id mapping + source metadata packing for the UI."""

from dataclasses import dataclass, field


@dataclass
class SourceRef:
    source: str
    chapter: str = ""
    verse: str = ""
    evidence_level: str = "classical"
    rights_url: str = ""


@dataclass
class Citations:
    refs: list[SourceRef] = field(default_factory=list)

    def add(self, ref: SourceRef) -> str:
        self.refs.append(ref)
        return f"[S{len(self.refs)}]"

    def to_payload(self) -> list[dict]:
        return [{"id": f"S{i+1}", "source": r.source, "chapter": r.chapter, "verse": r.verse,
                 "evidence_level": r.evidence_level, "rights_url": r.rights_url} for i, r in enumerate(self.refs)]