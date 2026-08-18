"""Model routing: primary -> live fallback with clean switch before first token."""

import logging
from collections.abc import Iterator

from app.config import get_settings

from .providers.gemini_provider import GeminiProvider
from .providers.openai_provider import OpenAIProvider

logger = logging.getLogger("rag.llm.router")

_PRIMARY = "primary"
_FALLBACK = "fallback"
_CHEAP = "cheap"


def _build_providers():
    s = get_settings()
    primary = OpenAIProvider(s.openai_api_key, s.llm_primary_model)
    fallback = GeminiProvider(s.gemini_api_key, s.llm_fallback_model)
    cheap = OpenAIProvider(s.openai_api_key, s.llm_cheap_model)
    return {_PRIMARY: primary, _FALLBACK: fallback, _CHEAP: cheap}


def get_provider(tier: str):
    return _build_providers()[tier]


def generate(messages: list[dict], tier: str = _PRIMARY, model: str | None = None) -> Iterator[str]:
    """Yield tokens. Tries primary first; switches to fallback only if the
    primary fails BEFORE the first token (avoids duplicate partial text).
    After streaming starts, a failure surfaces as an error event upstream.
    """
    providers = [get_provider(tier)]
    if tier == _PRIMARY:
        providers.append(get_provider(_FALLBACK))

    last_exc = None
    for provider in providers:
        try:
            stream = provider.generate(messages, model=model)
            first = next(stream)  # prime: first chunk decides which provider sticks
            yield first
            yield from stream
            return
        except StopIteration:
            return
        except Exception as exc:  # noqa: BLE001 - provider failover, handled below
            last_exc = exc
            logger.warning("Provider %s failed before first token: %s", provider.name, exc)
            continue
    raise last_exc  # type: ignore[misc]


def complete(messages: list[dict], tier: str = _PRIMARY, *, json_mode: bool = False, model: str | None = None) -> str:
    providers = [get_provider(tier)]
    if tier == _PRIMARY:
        providers.append(get_provider(_FALLBACK))
    last_exc = None
    for provider in providers:
        try:
            return provider.complete(messages, model=model, json_mode=json_mode)
        except Exception as exc:  # noqa: BLE001 - provider failover, handled below
            last_exc = exc
            continue
    raise last_exc  # type: ignore[misc]