"""Tests for the ingestion pipeline: chunker, loader, verifier, manifest, indexer."""

import json
from pathlib import Path

from app.ingestion.chunker import chunk_document
from app.ingestion.loader import load_raw_sources
from app.ingestion.manifest import digest_of, read_manifest, write_manifest
from app.ingestion.metadata import build_chunk_metadata, content_hash
from app.ingestion.verifier import get_corpus_status, verify_metadata, verify_source

VERSE_DOC = {
    "id": "cs:adhyaya-1",
    "source": "charaka_samhita",
    "chapter": "Sutrasthana 1",
    "content": (
        "1. Line of first shloka with quite a lot of words to fill space here.\n"
        "2. Second shloka continues the thought and adds more detail.\n"
        "3. Third shloka closes the section.\n"
        "\n"
        "This is prose commentary about the above verses. It goes on for a while "
        "explaining things in normal sentences without numbers."
    ),
    "evidence_level": "classical",
    "corpus_id": "charaka_samhita",
    "source_type": "CLASSICAL",
}


def test_verse_lines_are_never_split():
    chunks = chunk_document(VERSE_DOC, chunk_size=1000, overlap=100)
    for c in chunks:
        if c["metadata"]["verse"]:
            for line in c["content"].splitlines():
                if line.strip():
                    assert line[0].isdigit() or line.strip()[0] in "0123456789", f"verse line split: {line!r}"


def test_prose_coverage_is_complete():
    chunks = chunk_document(VERSE_DOC, chunk_size=6, overlap=2)
    prose = " ".join(c["content"] for c in chunks if not c["metadata"]["verse"])
    prose_words = set(VERSE_DOC["content"].split("\n\n", 1)[1].split())
    for w in prose_words:
        assert w in prose, f"lost word: {w}"


def test_no_verse_duplicated_across_chunks():
    chunks = chunk_document(VERSE_DOC, chunk_size=100, overlap=100)
    verse_lines = [line for c in chunks if c["metadata"]["verse"] for line in c["content"].splitlines() if line.strip()]
    assert len(verse_lines) == 3, f"expected 3 verse lines, got {len(verse_lines)}"


def test_chunk_metadata_contains_provenance():
    chunks = chunk_document(VERSE_DOC, chunk_size=1000, overlap=100)
    for c in chunks:
        meta = c["metadata"]
        assert "corpus_id" in meta, "missing corpus_id"
        assert "source_type" in meta, "missing source_type"
        assert "chunk_index" in meta, "missing chunk_index"
        assert meta["corpus_id"] == "charaka_samhita"
        assert meta["source_type"] == "CLASSICAL"


def test_chapter_boundaries_preserved():
    doc = {
        "id": "test:ch1",
        "source": "test_source",
        "chapter": "Chapter One",
        "content": "# Chapter One\nVerse 1 line.\nVerse 2 line.\n\nProse about chapter one.\n\n# Chapter Two\nDifferent verse line.\nMore prose here.",
        "evidence_level": "classical",
        "corpus_id": "test",
        "source_type": "GENERAL",
    }
    chunks = chunk_document(doc, chunk_size=1000, overlap=100)
    sources = {c["metadata"]["source"] for c in chunks}
    assert len(sources) == 1
    chapters = {c["metadata"]["chapter"] for c in chunks}
    assert "Chapter One" in chapters or "Chapter Two" in chapters


def test_empty_content_produces_no_chunks():
    doc = {
        "id": "test:empty",
        "source": "test",
        "chapter": "intro",
        "content": "",
        "evidence_level": "classical",
    }
    chunks = chunk_document(doc, chunk_size=100, overlap=10)
    assert chunks == []


# ---------------------------------------------------------------------------
# Verifier tests
# ---------------------------------------------------------------------------


def test_verify_source_legacy_format(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    (d / "rights_manifest.json").write_text(json.dumps({"rights": "public_domain", "license": "CC-BY-4.0"}))
    ok, _msg = verify_source(d)
    assert ok is True


def test_verify_source_extended_verified(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    (d / "rights_manifest.json").write_text(json.dumps({
        "rights_status": "PUBLIC_DOMAIN",
        "license": "CC-BY-4.0",
        "verification_status": "VERIFIED",
    }))
    ok, _msg = verify_source(d)
    assert ok is True


def test_verify_source_unknown_rights(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    (d / "rights_manifest.json").write_text(json.dumps({"rights_status": "UNKNOWN"}))
    ok, msg = verify_source(d)
    assert ok is False
    assert "UNKNOWN" in msg or "not allowed" in msg


def test_verify_source_missing_manifest(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    ok, msg = verify_source(d)
    assert ok is False
    assert "missing" in msg


def test_verify_metadata_valid(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    (d / "metadata.json").write_text(json.dumps({"corpus_id": "test", "title": "Test"}))
    ok, _msg = verify_metadata(d)
    assert ok is True


def test_verify_metadata_missing(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    ok, _msg = verify_metadata(d)
    assert ok is False


def test_get_corpus_status_not_available(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    assert get_corpus_status(d) == "NOT_AVAILABLE"


def test_get_corpus_status_ready(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    (d / "source.md").write_text("# Chapter 1\nSome content.\n")
    (d / "metadata.json").write_text(json.dumps({"corpus_id": "test", "title": "Test"}))
    (d / "rights_manifest.json").write_text(json.dumps({"rights": "public_domain", "license": "CC-BY"}))
    assert get_corpus_status(d) == "READY"


def test_get_corpus_status_rights_unverified(tmp_path):
    d = tmp_path / "test_src"
    d.mkdir()
    (d / "source.md").write_text("# Chapter 1\nSome content.\n")
    (d / "metadata.json").write_text(json.dumps({"corpus_id": "test", "title": "Test"}))
    assert get_corpus_status(d) == "RIGHTS_UNVERIFIED"


# ---------------------------------------------------------------------------
# Loader tests
# ---------------------------------------------------------------------------


def test_loader_skips_empty_dirs(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "empty_source").mkdir()
    docs = load_raw_sources(raw, verified_only=False)
    assert docs == []


def test_loader_splits_chapters(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    src = raw / "my_source"
    src.mkdir()
    (src / "source.md").write_text("# Chapter One\nContent one.\n\n# Chapter Two\nContent two.\n")
    docs = load_raw_sources(raw, verified_only=False)
    assert len(docs) == 2
    assert docs[0]["chapter"] == "Chapter One"
    assert docs[1]["chapter"] == "Chapter Two"


def test_loader_injects_metadata(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    src = raw / "my_source"
    src.mkdir()
    (src / "source.md").write_text("# Intro\nHello world.\n")
    (src / "metadata.json").write_text(json.dumps({"corpus_id": "my_src", "source_type": "CLASSICAL"}))
    docs = load_raw_sources(raw, verified_only=False)
    assert docs[0]["corpus_id"] == "my_src"
    assert docs[0]["source_type"] == "CLASSICAL"


# ---------------------------------------------------------------------------
# Manifest tests
# ---------------------------------------------------------------------------


def test_write_and_read_manifest(tmp_path):
    chunks = [{"content": "hello"}, {"content": "world"}]
    path = tmp_path / "manifest.json"
    write_manifest(path, version="test-v1", chunks=chunks, embedding_model="test-model", count=2, per_source={"src": 2})
    m = read_manifest(path)
    assert m["version"] == "test-v1"
    assert m["count"] == 2
    assert m["per_source"] == {"src": 2}
    assert "digest" in m
    assert "written_at" in m


def test_digest_is_deterministic():
    chunks = [{"content": "a"}, {"content": "b"}]
    d1 = digest_of(chunks)
    d2 = digest_of(chunks)
    assert d1 == d2


def test_read_manifest_missing():
    m = read_manifest(Path("/nonexistent"))
    assert m == {}


# ---------------------------------------------------------------------------
# Metadata builder tests
# ---------------------------------------------------------------------------


def test_build_chunk_metadata():
    meta = build_chunk_metadata(
        source="test",
        chapter="ch1",
        verse="v1",
        evidence_level="classical",
        corpus_id="test_corpus",
        source_type="CLASSICAL",
        chunk_index=5,
        rights_status="PUBLIC_DOMAIN",
    )
    assert meta["source"] == "test"
    assert meta["corpus_id"] == "test_corpus"
    assert meta["source_type"] == "CLASSICAL"
    assert meta["chunk_index"] == 5
    assert meta["rights_status"] == "PUBLIC_DOMAIN"


def test_content_hash_deterministic():
    h1 = content_hash("hello world")
    h2 = content_hash("hello world")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex digest


def test_content_hash_different_for_different_input():
    h1 = content_hash("hello")
    h2 = content_hash("world")
    assert h1 != h2
