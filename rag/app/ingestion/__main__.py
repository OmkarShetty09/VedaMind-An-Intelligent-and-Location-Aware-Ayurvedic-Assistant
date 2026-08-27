"""CLI entry point for corpus ingestion.

Usage:
    python -m app.ingestion status
    python -m app.ingestion ingest [--corpus CORPUS_ID]
    python -m app.ingestion validate [--corpus CORPUS_ID]
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("rag.ingestion.cli")

DATA_ROOT = Path(__file__).resolve().parents[3] / "data"


def cmd_status(args):
    from .indexer import scan_sources
    sources = scan_sources(DATA_ROOT / "raw")
    print(f"\n{'='*60}")
    print(f"{'CORPUS STATUS':^60}")
    print(f"{'='*60}")
    print(f"{'Source':<25} {'Status':<20} {'Rights':<10} {'Meta':<8} {'Size'}")
    print(f"{'-'*60}")
    for s in sources:
        size_kb = s["source_md_size"] / 1024
        print(f"{s['name']:<25} {s['status']:<20} {'OK' if s['rights_ok'] else 'NO':<10} {'OK' if s['metadata_ok'] else 'NO':<8} {size_kb:.1f}KB")
    print(f"{'='*60}")
    not_avail = sum(1 for s in sources if s["status"] == "NOT_AVAILABLE")
    ready = sum(1 for s in sources if s["status"] == "READY")
    print(f"Total: {len(sources)} | Ready: {ready} | Not Available: {not_avail}")
    if not_avail == len(sources):
        print("\n  No corpus sources have been provided yet.")
        print("  Place source.md files in data/raw/<source>/source.md")
        print("  See data/raw/*/metadata.json for expected content.")


def cmd_validate(args):
    from .indexer import scan_sources
    raw_dir = DATA_ROOT / "raw"
    sources = scan_sources(raw_dir)
    issues = []
    for s in sources:
        if s["status"] == "NOT_AVAILABLE":
            continue
        if not s["rights_ok"]:
            issues.append(f"  {s['name']}: {s['rights_msg']}")
        if not s["metadata_ok"]:
            issues.append(f"  {s['name']}: {s['metadata_msg']}")
    if issues:
        print("Validation issues:")
        for issue in issues:
            print(issue)
        sys.exit(1)
    else:
        available = [s for s in sources if s["status"] != "NOT_AVAILABLE"]
        print(f"All {len(available)} available sources validated successfully.")


def cmd_ingest(args):
    from .indexer import run_ingestion
    raw_dir = DATA_ROOT / "raw"
    chunks_dir = DATA_ROOT / "processed" / "chunks"
    manifest_path = DATA_ROOT / "processed" / "index_manifest.json"
    try:
        count = run_ingestion(
            raw_dir, chunks_dir, manifest_path,
            corpus_id=args.corpus,
        )
        print(f"\nIngestion complete: {count} chunks upserted.")
    except RuntimeError as e:
        print(f"\nIngestion failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_report(args):
    """Full report: status + DB chunk counts."""
    from .indexer import scan_sources
    sources = scan_sources(DATA_ROOT / "raw")
    print(f"\n{'='*60}")
    print(f"{'VEDAMIND RAG REPORT':^60}")
    print(f"{'='*60}")

    # Corpus status
    print("\n[CORPUS SOURCES]")
    for s in sources:
        status_marker = "✓" if s["status"] == "READY" else "✗" if s["status"] == "NOT_AVAILABLE" else "?"
        print(f"  {status_marker} {s['name']}: {s['status']}")

    # Manifest
    manifest_path = DATA_ROOT / "processed" / "index_manifest.json"
    if manifest_path.exists():
        from .manifest import read_manifest
        m = read_manifest(manifest_path)
        print("\n[MANIFEST]")
        print(f"  Embedding model: {m.get('embedding_model', 'unknown')}")
        print(f"  Total chunks: {m.get('count', 0)}")
        print(f"  Written: {m.get('written_at', 'unknown')}")
        per_source = m.get("per_source", {})
        if per_source:
            print("  Per source:")
            for src, cnt in sorted(per_source.items()):
                print(f"    {src}: {cnt}")
    else:
        print("\n[MANIFEST] Not found (no ingestion performed yet)")

    print(f"\n{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="VedaMind RAG Corpus Management")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show corpus source status")
    sub.add_parser("validate", help="Validate available sources")
    sub.add_parser("report", help="Full status report")

    ingest_p = sub.add_parser("ingest", help="Ingest corpus into pgvector")
    ingest_p.add_argument("--corpus", help="Only ingest this corpus ID")

    args = parser.parse_args()
    if args.command == "status":
        cmd_status(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "report":
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
