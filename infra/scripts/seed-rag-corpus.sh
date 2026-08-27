#!/usr/bin/env bash
set -euo pipefail

# Build the RAG index: data/raw -> chunks -> embeddings -> pgvector + manifest.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "==> Scanning corpus sources"
docker compose exec -T rag python -m app.ingestion status

echo ""
echo "==> Verifying corpus rights manifests"
docker compose exec -T rag python -m app.ingestion validate || {
    echo "Corpus validation failed. Fix the issues above before ingesting."
    exit 1
}

echo ""
echo "==> Ingesting corpus"
docker compose exec -T rag python -m app.ingestion ingest "$@"

echo ""
echo "==> Post-ingestion report"
docker compose exec -T rag python -m app.ingestion report

echo "Corpus ingested successfully."
