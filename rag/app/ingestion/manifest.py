"""index_manifest.json read/write - the corpus truth on disk."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def digest_of(chunks: list[dict]) -> str:
    blob = json.dumps([c["content"] for c in chunks], ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def write_manifest(
    path: Path,
    *,
    version: str,
    chunks: list[dict],
    embedding_model: str,
    count: int,
    per_source: dict[str, int] | None = None,
) -> dict:
    manifest = {
        "version": version,
        "embedding_model": embedding_model,
        "count": count,
        "digest": digest_of(chunks),
        "written_at": datetime.now(UTC).isoformat(),
        "per_source": per_source or {},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def read_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
