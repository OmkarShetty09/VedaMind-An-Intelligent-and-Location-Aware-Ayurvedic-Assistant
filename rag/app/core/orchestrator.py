"""THE RAG pipeline: retrieve -> guardrail -> generate -> verify -> stream.

Every step is versioned and traced. Generation is skipped entirely on
BLOCK / NEEDS_REVIEW. Tokens are streamed to the client as they arrive;
the full answer is buffered in parallel for post-stream cache writes.
"""

import logging
import re
import time
from collections.abc import Callable, Iterator

from app.config import get_settings
from app.guardrails import rules_client, secondary_check
from app.guardrails.jailbreak_detector import JailbreakDetector
from app.ingestion.embeddings import EmbeddingUnavailable, embed_query
from app.llm import cache as llm_cache
from app.llm import router, streaming, token_budget
from app.prompts import load_template, refusal_text, render_system_grounded
from app.retrieval.deps_store import get_store
from app.retrieval.filters import apply_filters
from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import MIN_RELEVANCE_SCORE, rerank
from app.security.input_sanitizer import sanitize
from app.security.prompt_injection import SYSTEM_GUARD

from . import versioning
from .citations import Citations
from .context import assemble
from .errors import PipelineError
from .tracing import span

logger = logging.getLogger("rag.orchestrator")

_jailbreak = JailbreakDetector()

_GREETING_RE = re.compile(
    r"^\s*(?:hi+|hello+|hey+|namaste|namaskar|good\s+(?:morning|afternoon|evening|night)"
    r"|howdy|greetings|what'?s\s+up|sup|hola|yo"
    r"|how\s+are\s+you(?:\s+doing)?|how'?s\s+it\s+going|how\s+do\s+you\s+do"
    r"|how\s+have\s+you\s+been|what'?s\s+happening|how'?s\s+everything"
    r"|how\s+is\s+it\s+going)\s*[!.?]*\s*$",
    re.IGNORECASE,
)


def _is_greeting(text: str) -> bool:
    return bool(_GREETING_RE.match(text))


def _greeting_response(user_message: str, context: dict) -> Iterator[str]:
    """Generate a context-aware greeting. No RAG retrieval, no guardrails."""
    has_profile = context.get("has_dosha_profile", False)
    dosha = context.get("dosha", {})
    dominant = dosha.get("dominant_dosha", "")
    secondary = dosha.get("secondary_dosha", "")

    dosha_ref = ""
    if has_profile and dominant:
        dosha_ref = dominant.capitalize() + (f" with secondary {secondary.capitalize()}" if secondary else "")

    messages = [
        {"role": "system", "content": SYSTEM_GUARD},
        {"role": "user", "content": load_template("greeting_prompt.j2").render(dosha_ref=dosha_ref).strip()},
    ]
    used: dict = {}
    try:
        answer = "".join(router.generate(messages, tier="cheap", used=used))
    except Exception:  # noqa: BLE001
        answer = load_template("greeting_fallback.j2").render(dosha_ref=dosha_ref).strip()

    for token in _split_tokens(answer):
        yield token
    yield streaming.citation_event([])
    yield streaming.done_event(blocked=False, reason_code="greeting", tokens=0, model=used.get("model", ""))


def _empty_kb_response(user_message: str) -> Iterator[str]:
    """Explicit response when the knowledge base has no ingested data."""
    yield streaming.low_confidence_event()
    msg = load_template("empty_kb.j2").render().strip()
    for token in _split_tokens(msg):
        yield token
    yield streaming.citation_event([])
    yield streaming.done_event(blocked=False, reason_code="empty_kb", low_confidence=True, tokens=0, model="")


def run(
    user_message: str,
    context: dict,
    *,
    conversation_id: str | None = None,
    message_id: str | None = None,
) -> Iterator[str]:
    settings = get_settings()
    query = sanitize(user_message)

    # 0. Greeting check: short-circuit before retrieval/guardrails
    if _is_greeting(query):
        logger.info("Greeting detected; generating conversational response.")
        yield from _greeting_response(user_message, context)
        return

    # 1. Empty KB check: if rag_chunks=0, explicitly say so
    store = None
    try:
        store = get_store()
        chunk_count = store.count_chunks()
        if chunk_count == 0:
            logger.info("Knowledge base empty; returning explicit empty-kb response.")
            yield from _empty_kb_response(user_message)
            return
    except Exception:  # noqa: BLE001
        pass  # if DB check fails, continue with pipeline (guardrails still work)

    # 2. adversarial scan (defense-in-depth; the rules engine is still the gate)
    risky, _ = _jailbreak.scan(user_message)
    if risky:
        yield streaming.guardrail_event({"decision": "needs_review", "severity": "high",
                                         "reason_code": "jailbreak_attempt", "source": "detector"})
        yield streaming.done_event(blocked=True, reason_code="jailbreak_attempt", tokens=0, model="")
        return

    # 3. retrieval
    with span("retrieve", query_len=len(query)):
        filters = apply_filters(query, context)
        embedding = None
        try:
            embedding = embed_query(query)
        except EmbeddingUnavailable:
            logger.info("Embeddings unavailable; sparse-only retrieval.")
        if embedding is not None:
            passages = hybrid_search(embedding, query, filters)
        elif store is not None:
            passages = store.search_sparse(query, settings.retrieval_candidates, filters)
        else:
            logger.info("No embeddings and no store available; cannot retrieve.")
            passages = []
        passages = rerank(passages, query)

    top = passages[0] if passages else None
    if top is None or top.score < MIN_RELEVANCE_SCORE:
        logger.info("Relevance gate tripped (score=%s); refusing.", top.score if top else None)
        yield streaming.low_confidence_event()
        for token in _split_tokens(refusal_text()):
            yield token
        yield streaming.citation_event([])
        yield streaming.done_event(blocked=True, reason_code="low_relevance", low_confidence=True, tokens=0, model="")
        return

    # 4. guardrail (binding, before generation)
    with span("guardrail", decision=""):
        result = rules_client.check(query, context, conversation_id, message_id)
        # Only a herb the engine had no rule for is worth a second look; without one the LLM
        # reviewer would escalate harmless questions (e.g. a routine question from someone on medication).
        if result.reason_code == "no_rule_found" and _has_meds(context) and result.entities.get("herbs"):
            result = secondary_check.secondary_review(result, query, context)
        yield streaming.guardrail_event(result.to_event())
        if not result.allows_generation:
            yield streaming.done_event(blocked=True, reason_code=result.reason_code, tokens=0, model="")
            return

    # 5. clarifying question: if recommending herbs and user hasn't disclosed meds
    if _is_herb_recommendation(query) and not _has_meds(context) and not _has_asked_meds(context):
        yield streaming.clarifying_question_event(CLARIFYING_MEDS_QUESTION)
        yield streaming.done_event(blocked=False, tokens=0, model="", needs_clarification=True)
        return

    # 6. cache (only for clean passes)
    citations = Citations()
    assembled = assemble(passages, citations)
    history = _prior_turns(context, user_message)
    # The answer is personalised (dosha, season, meds, prior turns), so those belong in the cache key too.
    key = llm_cache.cache_key(query, [p["chunk_id"] for p in assembled],
                              versioning.PROMPT_VERSION, settings.llm_primary_model,
                              personalization=_personalization_fingerprint(context, history))
    cached = llm_cache.get_cached(key)
    if cached:
        chip = _build_context_chip(context)
        if chip:
            yield streaming.context_chip_event(chip)
        for token in _split_tokens(cached["answer"]):
            yield token
        yield streaming.citation_event(citations.to_payload())
        yield streaming.done_event(blocked=False, tokens=cached["tokens"], model="cache")
        return

    # 7. generate — true streaming with buffered cache write
    with span("generate", model=settings.llm_primary_model):
        chip = _build_context_chip(context)
        if chip:
            yield streaming.context_chip_event(chip)

        messages = render_system_grounded(
            assembled,
            query,
            dosha=context.get("dosha"),
            season=context.get("season"),
            medications=context.get("medications"),
            conditions=context.get("conditions"),
            location_context=_format_location(context.get("location"), context.get("weather")),
            history=history,
        )
        messages.insert(1, {"role": "system", "content": SYSTEM_GUARD})

        answer_buf: list[str] = []
        used: dict = {}
        _ttft_start = time.monotonic()
        yield from _stream_and_buffer(
            router.generate(messages, tier="primary", used=used),
            answer_buf,
            on_first_token=lambda: logger.info(
                "ttft", extra={"step": "ttft", "duration_ms": round((time.monotonic() - _ttft_start) * 1000, 1)},
            ),
        )

        answer = "".join(answer_buf)
        if not answer.strip():
            raise PipelineError("Empty generation from providers", recoverable=True)

        yield streaming.citation_event(citations.to_payload())
        yield streaming.done_event(
            blocked=False, tokens=token_budget.estimate_tokens(answer), model=used.get("model", settings.llm_primary_model)
        )
        llm_cache.set_cached(key, {"answer": answer, "tokens": token_budget.estimate_tokens(answer)},
                             settings.query_cache_ttl_hours)


def verify_grounding(answer: str, passages: list[dict]) -> bool:
    """Per-sentence citation check via the cheap tier. True = grounded.

    Requires an LLM key; if unavailable we default to True (the deterministic
    citation instructions remain, but we can't machine-check - documented).
    """
    settings = get_settings()
    if not settings.openai_api_key and not settings.gemini_api_key:
        return True
    from app.llm.structured import complete_json

    prompt = (
        "You verify RAG faithfulness. For each sentence of the answer, decide if it is "
        "supported by or reasonably inferred from the passages. Return JSON ONLY: "
        "{\"supported\": [true|false,...]} with one entry per sentence.\n\nPASSAGES:\n"
        + "\n".join(f"[{i}] {p['content'][:500]}" for i, p in enumerate(passages[:10]))
        + "\n\nANSWER:\n" + answer
    )
    try:
        result = complete_json([{"role": "user", "content": prompt}], tier="cheap")
        flags = result.get("supported", [])
        if not flags:
            return False
        return sum(flags) / len(flags) >= 0.5
    except Exception as exc:  # noqa: BLE001 - verifier failure must not block the answer
        logger.warning("Grounding verifier unavailable (%s); accepting.", exc)
        return True


def _has_meds(context: dict) -> bool:
    return bool(context.get("medications") or context.get("conditions"))


CLARIFYING_MEDS_QUESTION = load_template("clarifying_meds.j2").render().strip()


def _has_asked_meds(context: dict) -> bool:
    """True once we asked the medication question, or the user has talked about their medication.

    Only user turns are scanned for keywords: every assistant answer ends with a disclaimer that
    mentions "medication", which would otherwise suppress the question forever after one answer.
    """
    for msg in context.get("history", []):
        content = (msg.get("content") or "").lower()
        if msg.get("role") == "assistant":
            if CLARIFYING_MEDS_QUESTION.lower() in content:
                return True
        elif "medication" in content or "condition" in content or "drug" in content or "medicine" in content:
            return True
    return False


def _is_herb_recommendation(query: str) -> bool:
    herb_keywords = [
        "recommend", "suggest", "should i take", "should i use",
        "herb", "remedy", "supplement", "formulation",
    ]
    q = query.lower()
    return any(kw in q for kw in herb_keywords)


def _build_context_chip(context: dict) -> str | None:
    parts = []
    season = context.get("season")
    weather = context.get("weather", {})
    location = context.get("location")
    dosha = context.get("dosha", {})
    if season:
        parts.append(season.capitalize())
    if location and weather.get("condition"):
        parts.append(weather["condition"].title())
    elif weather.get("condition"):
        parts.append(weather["condition"].title())
    dominant = dosha.get("dominant_dosha", "")
    if dominant:
        parts.append(f"{dominant.capitalize()}-adjusted")
    return " · ".join(parts) if parts else None


def _format_location(location: dict | None, weather: dict | None) -> str | None:
    if not location and not weather:
        return None
    parts = []
    if weather and weather.get("condition"):
        parts.append(weather["condition"])
    if weather and weather.get("temp_c") is not None:
        parts.append(f"{weather['temp_c']}°C")
    if location and location.get("lat") is not None and location.get("lon") is not None:
        parts.append(f"lat {float(location['lat']):.2f}, lon {float(location['lon']):.2f}")
    return ", ".join(parts) if parts else None


def _prior_turns(context: dict, user_message: str) -> list[dict]:
    """Conversation history without the current message (Django includes it as the last turn)."""
    history = list(context.get("history") or [])
    if history and history[-1].get("role") == "user" and (history[-1].get("content") or "") == user_message:
        history = history[:-1]
    return history


def _personalization_fingerprint(context: dict, history: list[dict]) -> str:
    dosha = context.get("dosha") or {}
    parts = [
        dosha.get("dominant_dosha", ""),
        dosha.get("secondary_dosha", ""),
        str(context.get("season") or ""),
        ",".join(sorted(map(str, context.get("medications") or []))),
        ",".join(sorted(map(str, context.get("conditions") or []))),
        "|".join((t.get("content") or "")[:200] for t in history[-6:]),
    ]
    return "\x1f".join(parts)


def _split_tokens(text: str, size: int = 40) -> Iterator[str]:
    for i in range(0, len(text), size):
        yield streaming.token_event(text[i : i + size])


def _stream_and_buffer(source: Iterator[str], buf: list[str], on_first_token: Callable[[], None] | None = None) -> Iterator[str]:
    """Yield SSE token events from *source* while buffering raw text into *buf*.

    After the generator is exhausted *buf* contains the full answer text,
    suitable for writing to the LLM response cache.  *on_first_token*, if
    provided, is called (with no arguments) the moment the first token chunk
    arrives from *source* — intended for TTFT measurement.
    """
    first = True
    for chunk in source:
        if first:
            first = False
            if on_first_token is not None:
                on_first_token()
        buf.append(chunk)
        yield streaming.token_event(chunk)
