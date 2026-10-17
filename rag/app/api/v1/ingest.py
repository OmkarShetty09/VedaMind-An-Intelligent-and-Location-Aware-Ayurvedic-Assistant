
from fastapi import APIRouter, Request

from app.config import get_settings
from app.ingestion.indexer import run_ingestion, corpus_status

router = APIRouter()



@router.post("/ingest")
def ingest(request: Request):
    """Trigger corpus ingestion: data/raw -> chunks -> embeddings -> store."""
    get_settings()
    raw = get_settings().data_dir / "raw"
    chunks = get_settings().data_dir / "processed" / "chunks"
    manifest_path = get_settings().data_dir / "processed" / "index_manifest.json"
    corpus_id = request.query_params.get("corpus")
    count = run_ingestion(raw, chunks, manifest_path, corpus_id=corpus_id)
    return {"status": "ok", "chunks": count, "corpus": corpus_id}


@router.get("/ingest/status")
def ingest_status():
    manifest = (get_settings().data_dir / "processed" / "index_manifest.json")
    from app.ingestion.manifest import read_manifest
    return {"manifest": read_manifest(manifest), "vector_store": get_settings().vector_store}


@router.get("/ingest/corpus-status")
def get_corpus_status():
    raw = get_settings().data_dir / "raw"
    manifest = get_settings().data_dir / "processed" / "index_manifest.json"
    return corpus_status(raw, manifest)
