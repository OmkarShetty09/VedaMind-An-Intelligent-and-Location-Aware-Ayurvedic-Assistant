"""Model routing: primary -> live fallback -> local fallback with clean switch before first token."""

import logging
from collections.abc import Iterator

from app.config import get_settings
from app.core.errors import ProviderError

from .providers.gemini_provider import GeminiProvider
from .providers.groq_provider import GroqProvider
from .providers.ollama_provider import OllamaProvider

logger = logging.getLogger("rag.llm.router")

_PRIMARY = "primary"
_FALLBACK = "fallback"
_LOCAL_FALLBACK = "local"
_CHEAP = "cheap"

# Failover order per tier. Primary falls through Groq (live) then Ollama (local).
_TIER_CHAIN = {
    _PRIMARY: [_PRIMARY, _FALLBACK, _LOCAL_FALLBACK],
    _CHEAP: [_CHEAP, _FALLBACK, _LOCAL_FALLBACK],
}


def _build_providers():
    s = get_settings()
    primary = GeminiProvider(s.gemini_api_key, s.llm_primary_model, s.llm_thinking_level)
    fallback = GroqProvider(s.groq_api_key, s.llm_fallback_model, base_url=s.groq_chat_url)
    local = OllamaProvider(default_model=s.llm_local_fallback_model, base_url=s.ollama_base_url)
    cheap = GeminiProvider(s.gemini_api_key, s.llm_cheap_model, s.llm_thinking_level)
    return {_PRIMARY: primary, _FALLBACK: fallback, _LOCAL_FALLBACK: local, _CHEAP: cheap}


def get_provider(tier: str):
    return _build_providers()[tier]


def generate(
    messages: list[dict], tier: str = _PRIMARY, model: str | None = None, used: dict | None = None
) -> Iterator[str]:
    """Yield tokens. Tries the tier chain in order; switches to the next provider
    only if the current one fails BEFORE the first token (avoids duplicate
    partial text). After streaming starts, a failure surfaces as an error event
    upstream. If `used` is given, it receives {"model": "<provider>/<model>"} of the
    provider that actually answered (for the audit trail).
    """
    providers = [get_provider(t) for t in _TIER_CHAIN.get(tier, [tier])]

    last_exc = None
    for provider in providers:
        try:
            stream = provider.generate(messages, model=model)
            first = next(stream)  # prime: first chunk decides which provider sticks
        except StopIteration:
            # Empty answer (e.g. a safety-filtered completion): nothing was sent yet, so fail over.
            last_exc = ProviderError("empty response", provider.name)
            logger.warning("Provider %s returned no text; trying next.", provider.name)
            continue
        except Exception as exc:  # noqa: BLE001 - provider failover, handled below
            last_exc = exc
            logger.warning("Provider %s failed before first token: %s", provider.name, exc)
            continue
        if used is not None:
            used["model"] = f"{provider.name}/{model or provider.default_model}"
        yield first
        yield from stream
        return
    raise last_exc  # type: ignore[misc]


def complete(messages: list[dict], tier: str = _PRIMARY, *, json_mode: bool = False, model: str | None = None) -> str:
    providers = [get_provider(t) for t in _TIER_CHAIN.get(tier, [tier])]
    last_exc = None
    for provider in providers:
        try:
            return provider.complete(messages, model=model, json_mode=json_mode)
        except Exception as exc:  # noqa: BLE001 - provider failover, handled below
            last_exc = exc
            logger.warning("Provider %s complete() failed: %s", provider.name, exc)
            continue
    raise last_exc  # type: ignore[misc]