"""Regression tests for the RAG fixes: provider payloads, prompt grounding, retrieval, caching, routing."""

import json

import httpx
import pytest

from app.config import usable_key
from app.core import orchestrator
from app.core.citations import Citations
from app.core.context import assemble
from app.core.errors import ProviderError
from app.guardrails import rules_client
from app.guardrails.decision import GuardrailResult
from app.llm import cache as llm_cache
from app.llm import router
from app.llm.providers import gemini_provider
from app.llm.providers.gemini_provider import GeminiProvider, _to_gemini_payload
from app.llm.providers.groq_provider import GroqProvider
from app.llm.providers.ollama_provider import OllamaProvider
from app.prompts import render_system_grounded
from app.retrieval.stores.base import Passage
from app.retrieval.stores.pgvector_store import _keyword_query

# ---------------------------------------------------------------- providers


def test_gemini_payload_moves_system_prompts_out_of_contents():
    payload = _to_gemini_payload(
        [
            {"role": "system", "content": "rules"},
            {"role": "system", "content": "guard"},
            {"role": "assistant", "content": "leading model turn"},
            {"role": "user", "content": "q1"},
            {"role": "user", "content": "q2"},
            {"role": "assistant", "content": "a1"},
        ]
    )
    assert payload["systemInstruction"]["parts"][0]["text"] == "rules\n\nguard"
    roles = [c["role"] for c in payload["contents"]]
    assert roles == ["user", "model"]  # no "system", opens with user, strictly alternating
    assert [p["text"] for p in payload["contents"][0]["parts"]] == ["q1", "q2"]


def test_gemini_skips_thought_parts():
    assert gemini_provider._answer_text([{"text": "thinking...", "thought": True}, {"text": "Answer"}]) == "Answer"


class _Resp:
    def __init__(self, status, body):
        self.status_code = status
        self._body = body
        self.text = json.dumps(body)

    def json(self):
        return self._body


def test_gemini_retries_without_unsupported_thinking_level(monkeypatch):
    gemini_provider._NO_THINKING_LEVEL.clear()
    sent = []

    def post(url, json, headers, timeout):
        sent.append(json)
        if "generationConfig" in json:
            return _Resp(400, {"error": {"message": "Thinking level MINIMAL is not supported for this model."}})
        return _Resp(200, {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})

    monkeypatch.setattr(gemini_provider.httpx, "post", post)
    provider = GeminiProvider("A" * 30, "gemini-x", thinking_level="minimal")
    assert provider.complete([{"role": "user", "content": "hi"}]) == "ok"
    assert sent[0]["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "minimal"}
    assert "generationConfig" not in sent[1]
    assert "gemini-x" in gemini_provider._NO_THINKING_LEVEL
    gemini_provider._NO_THINKING_LEVEL.clear()


def test_ollama_base_url_gets_chat_completions_path():
    assert OllamaProvider(base_url="http://127.0.0.1:11434/v1").base_url == "http://127.0.0.1:11434/v1/chat/completions"
    assert OllamaProvider(base_url="http://h:1/v1/chat/completions/").base_url == "http://h:1/v1/chat/completions"


@pytest.mark.parametrize("key", ["", "your-groq-api-key", "your-gemini-api-key", "sk-...", "change-me", "short"])
def test_placeholder_keys_are_not_usable(key):
    assert not usable_key(key)


def test_real_looking_key_is_usable():
    assert usable_key("gsk_" + "x" * 40)


def test_unconfigured_groq_fails_fast_without_http(monkeypatch):
    monkeypatch.setattr(httpx, "stream", lambda *a, **k: pytest.fail("must not call the API"))
    with pytest.raises(ProviderError):
        next(GroqProvider("your-groq-api-key", "m").generate([{"role": "user", "content": "x"}]))


class _FakeProvider:
    def __init__(self, name, tokens=None, exc=None):
        self.name = name
        self.default_model = f"{name}-model"
        self._tokens, self._exc = tokens or [], exc

    def generate(self, messages, model=None):
        if self._exc:
            raise self._exc
        yield from self._tokens


def test_router_fails_over_on_empty_stream_and_reports_the_answering_model(monkeypatch):
    chain = {
        "primary": _FakeProvider("gemini"),  # empty answer (e.g. safety-filtered)
        "fallback": _FakeProvider("groq", exc=ProviderError("503", "groq")),
        "local": _FakeProvider("ollama", tokens=["Va", "ta"]),
    }
    monkeypatch.setattr(router, "get_provider", lambda tier: chain[tier])
    used = {}
    assert "".join(router.generate([], tier="primary", used=used)) == "Vata"
    assert used["model"] == "ollama/ollama-model"


def test_router_raises_last_error_when_every_provider_fails(monkeypatch):
    monkeypatch.setattr(router, "get_provider", lambda tier: _FakeProvider(tier, exc=ProviderError("down", tier)))
    with pytest.raises(ProviderError):
        list(router.generate([], tier="primary"))


# ---------------------------------------------------------------- prompt + context


def test_prompt_contains_the_passage_text():
    # The template used {{ p.text }} while passages carry "content": the LLM saw no source text at all.
    messages = render_system_grounded(
        [{"chunk_id": "c1", "content": "Abhyanga is daily oil massage.", "metadata": {"source": "charaka_samhita"}}],
        "What is abhyanga?",
    )
    assert "[S1] Abhyanga is daily oil massage." in messages[0]["content"]


def test_prompt_includes_prior_turns_in_order():
    history = [{"role": "user", "content": "What is vata?"}, {"role": "assistant", "content": "Air and space."}]
    messages = render_system_grounded([], "And pitta?", history=history)
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]
    assert "What is vata?" in messages[1]["content"]


def test_answer_disclaimer_does_not_count_as_having_asked_about_medication():
    disclaimer = {"role": "assistant", "content": "...especially alongside existing medication."}
    assert not orchestrator._has_asked_meds({"history": [disclaimer]})
    asked = {"role": "assistant", "content": orchestrator.CLARIFYING_MEDS_QUESTION}
    assert orchestrator._has_asked_meds({"history": [disclaimer, asked]})
    assert orchestrator._has_asked_meds({"history": [{"role": "user", "content": "I take no medication"}]})


def test_prior_turns_excludes_the_current_message():
    context = {"history": [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"},
                           {"role": "user", "content": "now"}]}
    assert orchestrator._prior_turns(context, "now") == context["history"][:2]


def test_citations_only_cover_passages_that_fit_the_budget(monkeypatch):
    from app.config import get_settings

    monkeypatch.setenv("CONTEXT_MAX_TOKENS", "30")
    get_settings.cache_clear()
    passages = [Passage(f"c{i}", "word " * 40, {"source": f"s{i}"}, 1.0) for i in range(3)]
    passages[0] = Passage("c0", "short passage", {"source": "s0"}, 1.0)
    citations = Citations()
    kept = assemble(passages, citations)
    assert len(kept) == len(citations.refs) == 1


def test_cache_key_depends_on_personalisation():
    base = ("what is good for me", ["c1"], "v2", "m")
    assert llm_cache.cache_key(*base, personalization="vata") != llm_cache.cache_key(*base, personalization="kapha")
    vata = orchestrator._personalization_fingerprint({"dosha": {"dominant_dosha": "vata"}}, [])
    kapha = orchestrator._personalization_fingerprint({"dosha": {"dominant_dosha": "kapha"}}, [])
    assert vata != kapha


def test_keyword_query_ors_words_for_sparse_search():
    assert _keyword_query("What helps Vata in winter?") == "what or helps or vata or in or winter"
    assert _keyword_query("salt or sugar") == "salt or sugar"
    assert _keyword_query("!!!") == ""


# ---------------------------------------------------------------- guardrail client + orchestration


def test_rules_client_forwards_medications(monkeypatch):
    captured = {}

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"decision": "pass", "severity": "none", "reason_code": "no_rule_found", "matches": [],
                    "entities": {"herbs": ["turmeric"], "drugs": ["warfarin"]}}

    def post(url, json, headers, timeout):
        captured.update(json)
        return Resp()

    monkeypatch.setattr(rules_client.httpx, "post", post)
    result = rules_client.check("turmeric?", {"medications": ["warfarin 5 mg"]})
    assert captured["context"]["medications"] == ["warfarin 5 mg"]
    assert result.entities["herbs"] == ["turmeric"]


def test_guardrail_event_includes_matches_for_the_banner():
    event = GuardrailResult("block", "high", "interaction_high_or_severe",
                            [{"pair": "turmeric <-> warfarin", "recommendation": "Avoid.", "severity": "HIGH"}]).to_event()
    assert event["matches"] == [{"pair": "turmeric <-> warfarin", "recommendation": "Avoid."}]


class _Store:
    def count_chunks(self):
        return 10

    def search_sparse(self, q, k, f=None):
        return []


def test_secondary_review_skipped_when_no_herb_is_involved(monkeypatch):
    monkeypatch.setattr(orchestrator, "get_store", lambda: _Store())
    monkeypatch.setattr(orchestrator, "embed_query", lambda q: [0.1])
    monkeypatch.setattr(orchestrator, "hybrid_search",
                        lambda e, q, f: [Passage("c1", "Wake before sunrise.", {"source": "s"}, 0.9)])
    monkeypatch.setattr(orchestrator, "rerank", lambda ps, q: ps)
    monkeypatch.setattr(orchestrator.rules_client, "check",
                        lambda *a: GuardrailResult("pass", "none", "no_rule_found", [], entities={"herbs": []}))
    monkeypatch.setattr(orchestrator.secondary_check, "secondary_review",
                        lambda *a: pytest.fail("secondary review must not run without a herb"))
    monkeypatch.setattr(orchestrator.router, "generate", lambda messages, tier, **kw: iter(["Rise early [S1]."]))
    monkeypatch.setattr(llm_cache, "get_cached", lambda key: None)
    monkeypatch.setattr(llm_cache, "set_cached", lambda key, payload, ttl: None)

    events = [json.loads(e[6:]) for e in orchestrator.run("what is a good morning routine", {"medications": ["x"]})]
    assert next(e for e in events if e["type"] == "done")["blocked"] is False


def test_citations_carry_title_link_passage_and_references():
    citations = Citations()
    text = "Ashwagandha is a rasayana. See https://pubmed.ncbi.nlm.nih.gov/123/ and https://ayurwiki.org/x."
    assemble([Passage("c0", text, {"source": "ayurwiki_herbs", "chapter": "Withania  somnifera"}, 1.0),
              Passage("c1", "Langhana for jwara.", {"source": "ashtanga_hridaya", "chapter": "Jwara"}, 0.9)],
             citations)
    herbs, classical = citations.to_payload()
    assert herbs["title"].startswith("Ayurwiki Herbs")
    assert herbs["url"] == "https://ayurwiki.org/index.php?title=Special:Search&go=Go&search=Withania+somnifera"
    assert herbs["excerpt"] == text
    assert herbs["references"] == ["https://pubmed.ncbi.nlm.nih.gov/123/", "https://ayurwiki.org/x"]
    assert herbs["license"] == "CC BY-SA 4.0"
    # No public URL for this corpus: no link, but the full passage is still there to read.
    assert classical["url"] == "" and classical["excerpt"] == "Langhana for jwara."
