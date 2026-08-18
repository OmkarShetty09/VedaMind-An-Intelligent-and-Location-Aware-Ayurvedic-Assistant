
from app.retrieval.reranker import MIN_RELEVANCE_SCORE, rerank
from app.retrieval.stores.base import Passage


def make_passage(chunk_id, text, score):
    return Passage(chunk_id=chunk_id, text=text, metadata={"source": "x"}, score=score)


def test_rerank_preserves_order_when_disabled():
    passages = [make_passage("a", "first", 0.9), make_passage("b", "second", 0.1)]
    out = rerank(passages, "query")
    assert [p.chunk_id for p in out] == ["a", "b"]


def test_top_k_applied():
    passages = [make_passage(str(i), f"text {i}", 0.5) for i in range(10)]
    assert len(rerank(passages, "q")) == 8


def test_relevance_gate_constant_sane():
    assert 0.0 < MIN_RELEVANCE_SCORE < 1.0