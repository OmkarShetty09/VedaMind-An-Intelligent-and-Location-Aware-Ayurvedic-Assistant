"""Tests for retrieval source type classification and empty KB behavior."""

import json

from app.core import orchestrator
from app.guardrails.decision import GuardrailResult
from app.retrieval.stores.base import Passage


def passage(chunk_id, score, source_type="CLASSICAL", corpus_id="charaka_samhita"):
    return Passage(
        chunk_id=chunk_id,
        text="Some classical passage about the herb.",
        metadata={"source": "s", "source_type": source_type, "corpus_id": corpus_id},
        score=score,
    )


def collect(events):
    return [json.loads(e[len("data: ") :]) for e in events]


def test_empty_kb_returns_explicit_message(monkeypatch):
    """When rag_chunks=0, orchestrator returns explicit empty-kb message."""

    class FakeStore:
        def count_chunks(self):
            return 0
        def count_by_source(self):
            return []

    monkeypatch.setattr(orchestrator, "get_store", lambda: FakeStore())

    events = list(orchestrator.run("what is ashwagandha?", {}))
    parsed = collect(events)
    done = next(e for e in parsed if e["type"] == "done")
    assert done["reason_code"] == "empty_kb"
    tokens = "".join(e["delta"] for e in parsed if e["type"] == "token")
    assert "not yet been populated" in tokens.lower() or "knowledge base" in tokens.lower()


def test_nonempty_kb_proceeds_to_retrieval(monkeypatch):
    """When rag_chunks > 0, orchestrator proceeds with retrieval (not empty_kb)."""
    from app.llm import cache as llm_cache

    class FakeStore:
        def count_chunks(self):
            return 100
        def count_by_source(self):
            return [("test", 100)]
        def search_sparse(self, q, k, f=None):
            return [passage("c1", 0.9)]

    monkeypatch.setattr(orchestrator, "get_store", lambda: FakeStore())
    monkeypatch.setattr(orchestrator, "embed_query", lambda q: [0.5] * 8)
    monkeypatch.setattr(orchestrator, "hybrid_search", lambda e, q, f: [passage("c1", 0.9)])
    monkeypatch.setattr(orchestrator, "rerank", lambda ps, q: ps)
    monkeypatch.setattr(orchestrator.rules_client, "check", lambda *a: GuardrailResult("pass", "low", "no_match", []))
    monkeypatch.setattr(orchestrator, "render_system_grounded", lambda items, user, **kw: [{"role": "system", "content": ""}])
    monkeypatch.setattr(orchestrator.router, "generate", lambda messages, tier: "Answer based on passage [S1].")
    monkeypatch.setattr(orchestrator, "verify_grounding", lambda a, p: True)
    monkeypatch.setattr(llm_cache, "get_cached", lambda key: None)
    monkeypatch.setattr(llm_cache, "set_cached", lambda key, payload, ttl: None)

    events = list(orchestrator.run("what is ashwagandha?", {}))
    parsed = collect(events)
    # Should NOT have empty_kb reason
    assert not any(e.get("reason_code") == "empty_kb" for e in parsed)
    done = next(e for e in parsed if e["type"] == "done")
    assert done["blocked"] is False


def test_source_type_in_passage_metadata():
    """Verify source_type is carried through passage metadata."""
    p = passage("c1", 0.9, source_type="MODERN_CLINICAL", corpus_id="clinical_evidence")
    assert p.metadata["source_type"] == "MODERN_CLINICAL"
    assert p.metadata["corpus_id"] == "clinical_evidence"
