"""Offline eval harness. Run: python -m app.evaluation.harness --set curated

Reads eval set JSON, replays the pipeline (retrieval-only by default; use
--with-generation to also score answers via the cheap LLM).
"""

import argparse
import json
import logging
from pathlib import Path

from app.config import get_settings
from app.ingestion.embeddings import EmbeddingUnavailable, embed_query
from app.retrieval.deps_store import get_store
from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import rerank

from .metrics import coverage, precision

logger = logging.getLogger("rag.evaluation")

EVAL_ROOT = Path(__file__).resolve().parents[4] / "eval" / "sets"


def load_set(name: str) -> list[dict]:
    path = EVAL_ROOT / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Eval set '{name}' not found in {EVAL_ROOT}")
    return json.loads(path.read_text(encoding="utf-8"))


def run_retrieval_eval(set_name: str) -> dict:
    settings = get_settings()
    store = get_store()
    items = load_set(set_name)
    agg = {"coverage": [], "precision": [], "answerable": []}
    for item in items:
        query = item["query"]
        gold = set(item["relevant_chunk_ids"])
        try:
            emb = embed_query(query)
            passages = hybrid_search(emb, query, {})
        except EmbeddingUnavailable:
            passages = store.search_sparse(query, settings.retrieval_candidates, {})
        passages = rerank(passages, query)
        retrieved = {p.chunk_id for p in passages}
        agg["coverage"].append(coverage(retrieved, gold))
        agg["precision"].append(precision(retrieved, gold))
        agg["answerable"].append(1.0 if item.get("expected") else 0.0)
    return {k: (sum(v) / len(v) if v else 0.0) for k, v in agg.items()}


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", default="curated")
    args = parser.parse_args()
    results = run_retrieval_eval(args.set)
    logger.info("Eval results: %s", results)


if __name__ == "__main__":
    main()