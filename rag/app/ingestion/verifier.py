"""License/rights gate: no source is ingested without a verified manifest.

Supports two manifest formats:
1. Legacy: {"rights": "public_domain", "license": "..."}
2. Extended: {"rights_status": "...", "license": "...", "verification_status": "..."}

Only sources with verified rights are ingested.
"""

import json
from pathlib import Path

ALLOWED_STATUSES = {"public_domain", "cc_by", "licensed"}
ALLOWED_EXTENDED_STATUSES = {"VERIFIED"}  # only VERIFIED sources pass


def verify_source(source_dir: Path) -> tuple[bool, str]:
    """Check rights_manifest.json and metadata.json for a corpus source."""
    manifest = source_dir / "rights_manifest.json"
    if not manifest.exists():
        return False, f"{manifest.name} missing for {source_dir.name}"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, f"{manifest.name} is invalid JSON for {source_dir.name}"

    # Extended format: check verification_status
    verification = data.get("verification_status", "").upper()
    if verification in ALLOWED_EXTENDED_STATUSES:
        return True, "ok"

    # Extended format: check rights_status
    rights_status = data.get("rights_status", "").upper()
    if rights_status in {"PUBLIC_DOMAIN", "CC_BY", "LICENSED"}:
        if not data.get("license"):
            return False, f"license field missing for {source_dir.name}"
        return True, "ok"

    # Legacy format: check "rights" key
    status = (data.get("rights") or "").lower()
    if status in ALLOWED_STATUSES:
        if not data.get("license"):
            return False, f"license field missing for {source_dir.name}"
        return True, "ok"

    return False, f"rights '{rights_status or status}' not allowed for {source_dir.name}"


def verify_metadata(source_dir: Path) -> tuple[bool, str]:
    """Verify metadata.json exists and is valid."""
    meta_path = source_dir / "metadata.json"
    if not meta_path.exists():
        return False, f"metadata.json missing for {source_dir.name}"
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, f"metadata.json is invalid JSON for {source_dir.name}"
    if not data.get("corpus_id"):
        return False, f"corpus_id missing in metadata.json for {source_dir.name}"
    return True, "ok"


def get_corpus_status(source_dir: Path) -> str:
    """Determine the corpus status for a source directory."""
    source_md = source_dir / "source.md"
    meta_path = source_dir / "metadata.json"
    rights_path = source_dir / "rights_manifest.json"

    if not source_md.exists() or source_md.stat().st_size == 0:
        return "NOT_AVAILABLE"
    if not meta_path.exists():
        return "NOT_AVAILABLE"
    if not rights_path.exists():
        return "RIGHTS_UNVERIFIED"

    meta_ok, _ = verify_metadata(source_dir)
    rights_ok, _ = verify_source(source_dir)

    if not meta_ok:
        return "FAILED"
    if not rights_ok:
        return "RIGHTS_UNVERIFIED"
    return "READY"
