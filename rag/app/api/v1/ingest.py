from pathlib import Path

from fastapi import APIRouter

from app.config import get_settings
from app.ingestion.indexer import run_ingestion
from app.ingestion.manifest import read_manifest

router = APIRouter()

DATA_ROOT = Path(__file__).resolve().parents[4] / "data"


@router.post("/ingest")
def ingest():
    """Trigger corpus ingestion: data/raw -> chunks -> embeddings -> store."""
    get_settings()
    raw = DATA_ROOT / "raw"
    chunks = DATA_ROOT / "processed" / "chunks"
    manifest_path = DATA_ROOT / "processed" / "index_manifest.json"
    count = run_ingestion(raw, chunks, manifest_path)
    return {"status": "ok", "chunks": count}


@router.get("/ingest/status")
def ingest_status():
    manifest = read_manifest(DATA_ROOT / "processed" / "index_manifest.json")
    return {"manifest": manifest, "vector_store": get_settings().vector_store}