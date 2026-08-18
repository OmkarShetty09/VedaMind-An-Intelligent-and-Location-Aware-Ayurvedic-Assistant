#!/usr/bin/env bash
set -euo pipefail

# Build the RAG index: data/raw -> chunks -> embeddings -> pgvector + manifest.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "==> Verifying corpus rights manifests"
python - <<'PY'
import json, sys
from pathlib import Path
raw = Path("data/raw")
ok = True
for d in sorted(raw.iterdir()):
    if not d.is_dir():
        continue
    m = d / "rights_manifest.json"
    if not m.exists():
        print(f"MISSING manifest: {d.name}")
        ok = False
        continue
    data = json.loads(m.read_text())
    if data.get("rights") not in ("public_domain", "cc_by", "licensed"):
        print(f"BLOCKED rights: {d.name}")
        ok = False
if not ok:
    sys.exit("Corpus has unverified sources; refusing to ingest.")
PY

echo "==> Ingesting corpus"
docker compose exec -T rag python - <<'PY'
from app.ingestion.indexer import run_ingestion
from pathlib import Path
raw = Path("data/raw")
run_ingestion(raw, Path("data/processed/chunks"), Path("data/processed/index_manifest.json"))
PY

echo "Corpus ingested."
