"""License/rights gate: no source is ingested without a proven manifest.

This is the corpus safety valve (Section 3.1). Blocking here is cheaper and
safer than removing a violated text later.
"""

import json
from pathlib import Path

ALLOWED_STATUSES = {"public_domain", "cc_by", "licensed"}


def verify_source(source_dir: Path) -> tuple[bool, str]:
    manifest = source_dir / "rights_manifest.json"
    if not manifest.exists():
        return False, f"{manifest.name} missing for {source_dir.name}"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, f"{manifest.name} is invalid JSON"
    status = (data.get("rights") or "").lower()
    if status not in ALLOWED_STATUSES:
        return False, f"rights '{status}' not allowed for {source_dir.name}"
    if not data.get("license"):
        return False, f"license field missing for {source_dir.name}"
    return True, "ok"