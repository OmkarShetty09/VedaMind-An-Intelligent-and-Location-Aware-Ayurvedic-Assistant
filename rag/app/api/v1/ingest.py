from pathlib import Path

from fastapi import APIRouter, Request

from app.config import get_settings
from app.ingestion.indexer import run_ingestion, corpus_status

router = APIRouter()

DATA_ROOT = Path(__file__).resolve().parents[4] / "data"


@router.post("/ingest")
def ingest(request: Request):
    """Trigger corpus ingestion: data/raw -> chunks -> embeddings -> store."""
    get_settings()
    raw = DATA_ROOT / "raw"
    chunks = DATA_ROOT / "processed" / "chunks"
    manifest_path = DATA_ROOT / "processed" / "index_manifest.json"
    corpus_id = request.query_params.get("corpus")
    count = run_ingestion(raw, chunks, manifest_path, corpus_id=corpus_id)
    return {"status": "ok", "chunks": count, "corpus": corpus_id}


@router.get("/ingest/status")
def ingest_status():
    manifest = (DATA_ROOT / "processed" / "index_manifest.json")
    from app.ingestion.manifest import read_manifest
    return {"manifest": read_manifest(manifest), "vector_store": get_settings().vector_store}


@router.get("/ingest/corpus-status")
def get_corpus_status():
    raw = DATA_ROOT / "raw"
    manifest = DATA_ROOT / "processed" / "index_manifest.json"
    return corpus_status(raw, manifest)
