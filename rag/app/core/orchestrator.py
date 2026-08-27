"""THE RAG pipeline: retrieve -> guardrail -> generate -> verify -> stream.

Every step is versioned and traced. Generation is skipped entirely on
BLOCK / NEEDS_REVIEW. Answers are buffered and grounding-verified BEFORE any
token reaches the user (safety over raw streaming latency).
"""

import logging
import re
from collections.abc import Iterator

from app.config import get_settings
from app.guardrails import rules_client, secondary_check
from app.guardrails.jailbreak_detector import JailbreakDetector
from app.ingestion.embeddings import EmbeddingUnavailable, embed_query
from app.llm import cache as llm_cache
from app.llm import router, streaming, token_budget
from app.prompts import refusal_text, render_system_grounded
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
    r"^\s*(?:hi|hello|hey|namaste|namaskar|good\s+(?:morning|afternoon|evening|night)"
    r"|howdy|greetings|what'?s\s+up|sup|hola|yo)\s*[!.?]*\s*$",
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

    if has_profile and dominant:
        dosha_ref = dominant.capitalize()
        if secondary:
            dosha_ref += f" with secondary {secondary.capitalize()}"
        prompt = (
            "You are VedaMind, a personalized Ayurvedic wellness assistant. "
            "The user has greeted you. They already have a completed Prakriti assessment: "
            f"their constitution is {dosha_ref}. "
            "Greet them warmly, briefly reference their existing dosha profile, "
            "and ask how you can help them today. "
            "Keep it to 1-2 sentences. Do not give unsolicited health advice."
        )
    else:
        prompt = (
            "You are VedaMind, a personalized Ayurvedic wellness assistant. "
            "The user has greeted you. They do not yet have a Prakriti (dosha) profile. "
            "Greet them warmly, briefly introduce yourself, explain that a short "
            "Prakriti assessment is needed before you can give personalized guidance, "
            "and ask whether they would like to begin. "
            "Keep it to 2-3 sentences. Do not give unsolicited health advice."
        )

    messages = [
        {"role": "system", "content": SYSTEM_GUARD},
        {"role": "user", "content": prompt},
    ]

    try:
        answer = "".join(router.generate(messages, tier="cheap"))
    except Exception:  # noqa: BLE001
        if has_profile and dominant:
            answer = (
                f"Hi! Good to see you again. Since you're primarily {dominant.capitalize()}"
                + (f" with secondary {secondary.capitalize()}" if secondary else "")
                + ", I can tailor my Ayurvedic guidance to you. What would you like help with today?"
            )
        else:
            answer = (
                "Hi! I'm VedaMind, your personalized Ayurvedic wellness assistant. "
                "Before I give you personalized guidance, I'd like to understand your "
                "Ayurvedic constitution through a few simple questions. Would you like to begin?"
            )

    for token in _split_tokens(answer):
        yield token
    yield streaming.citation_event([])
    yield streaming.done_event(blocked=False, reason_code="greeting", tokens=0, model="cheap")


def _empty_kb_response(user_message: str) -> Iterator[str]:
    """Explicit response when the knowledge base has no ingested data."""
    yield streaming.low_confidence_event()
    msg = (
        "I don't have sufficient classical sources to answer this question. "
        "The Ayurvedic knowledge base has not yet been populated with source texts. "
        "Please consult a qualified Ayurvedic practitioner for personalized guidance."
    )
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
        else:
            passages = store.search_sparse(query, settings.retrieval_candidates, filters)
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
        if result.reason_code == "no_rule_found" and _has_meds(context):
            result = secondary_check.secondary_review(result, query, context)
        yield streaming.guardrail_event(result.to_event())
        if not result.allows_generation:
            yield streaming.done_event(blocked=True, reason_code=result.reason_code, tokens=0, model="")
            return

    # 5. clarifying question: if recommending herbs and user hasn't disclosed meds
    if _is_herb_recommendation(query) and not _has_meds(context) and not _has_asked_meds(context):
        yield streaming.clarifying_question_event(
            "Are you currently on any medication or have any diagnosed condition I should factor in?"
        )
        yield streaming.done_event(blocked=False, tokens=0, model="", needs_clarification=True)
        return

    # 6. cache (only for clean passes)
    citations = Citations()
    assembled = assemble(passages, citations)
    key = llm_cache.cache_key(query, [p["chunk_id"] for p in assembled],
                              versioning.PROMPT_VERSION, settings.llm_primary_model)
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

    # 7. generate (buffered, then verified)
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
        )
        messages.insert(1, {"role": "system", "content": SYSTEM_GUARD})
        answer = "".join(router.generate(messages, tier="primary"))
        if not answer.strip():
            raise PipelineError("Empty generation from providers", recoverable=True)

    # 8. grounding verification (skip when no LLM configured)
    with span("verify"):
        grounded = verify_grounding(answer, assembled)
        if not grounded:
            logger.warning("Grounding verification failed; replacing with refusal.")
            yield streaming.low_confidence_event()
            answer = refusal_text()

    for token in _split_tokens(answer):
        yield token
    yield streaming.citation_event(citations.to_payload())
    yield streaming.done_event(blocked=False, tokens=token_budget.estimate_tokens(answer), model=settings.llm_primary_model)
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
        "supported by the passages. Return JSON ONLY: {\"supported\": [true|false,...]} "
        "with one entry per sentence.\n\nPASSAGES:\n"
        + "\n".join(f"[{i}] {p['content']}" for i, p in enumerate(passages[:6]))
        + "\n\nANSWER:\n" + answer
    )
    try:
        result = complete_json([{"role": "user", "content": prompt}], tier="cheap")
        flags = result.get("supported", [])
        if not flags:
            return False
        return sum(flags) / len(flags) >= 0.7
    except Exception as exc:  # noqa: BLE001 - verifier failure must not block the answer
        logger.warning("Grounding verifier unavailable (%s); accepting.", exc)
        return True


def _has_meds(context: dict) -> bool:
    return bool(context.get("medications") or context.get("conditions"))


def _has_asked_meds(context: dict) -> bool:
    history = context.get("history", [])
    for msg in history:
        content = (msg.get("content") or "").lower()
        if "medication" in content or "condition" in content or "drug" in content:
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
    if location:
        parts.append(f"lat {location['lat']:.2f}, lon {location['lon']:.2f}")
    return ", ".join(parts) if parts else None


def _split_tokens(text: str, size: int = 40) -> Iterator[str]:
    for i in range(0, len(text), size):
        yield streaming.token_event(text[i : i + size])
