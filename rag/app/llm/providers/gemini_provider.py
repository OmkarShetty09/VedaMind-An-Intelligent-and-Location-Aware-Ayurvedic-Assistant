import json
import logging

import httpx

from app.config import get_settings, usable_key
from app.core.errors import ProviderError

from .base import LLMProvider

logger = logging.getLogger("rag.llm.gemini")



def _to_gemini_payload(messages: list[dict]) -> dict:
    """OpenAI-style messages -> Gemini request body.

    Gemini `contents` only accepts the roles "user" and "model"; system prompts go in
    `systemInstruction` (sending role "system" in contents is rejected with HTTP 400).
    """
    system = [m["content"] for m in messages if m["role"] == "system" and m.get("content")]
    contents: list[dict] = []
    for m in messages:
        if m["role"] == "system" or not m.get("content"):
            continue
        role = "model" if m["role"] == "assistant" else "user"
        if not contents and role == "model":
            continue  # a conversation must open with a user turn
        if contents and contents[-1]["role"] == role:
            contents[-1]["parts"].append({"text": m["content"]})  # turns must alternate
        else:
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
    payload = {"contents": contents}
    if system:
        payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system)}]}
    return payload


def _error_detail(resp: httpx.Response) -> str:
    try:
        return resp.json().get("error", {}).get("message", "")[:300]
    except ValueError:
        return resp.text[:300]


def _answer_text(parts: list[dict]) -> str:
    # Thinking models may return thought summaries as parts flagged `thought`; they are not the answer.
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


# Models that answered "Thinking level ... is not supported" - they get the model's default from then on.
_NO_THINKING_LEVEL: set[str] = set()


def _rejects_thinking_level(resp: httpx.Response) -> bool:
    return resp.status_code == 400 and "thinking level" in _error_detail(resp).lower()


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, default_model: str, thinking_level: str = ""):
        self._api_key = api_key
        self.default_model = default_model
        # Gemini 3 models think before answering by default (several seconds before the first token);
        # "minimal" keeps chat responsive. Levels differ per model, so a rejected level falls back to default.
        self.thinking_level = thinking_level

    def _payload(self, messages, model: str, *, json_mode: bool = False) -> dict:
        payload = _to_gemini_payload(messages)
        config = {}
        if json_mode:
            config["responseMimeType"] = "application/json"
        if self.thinking_level and model not in _NO_THINKING_LEVEL:
            config["thinkingConfig"] = {"thinkingLevel": self.thinking_level}
        if config:
            payload["generationConfig"] = config
        return payload

    def generate(self, messages, model=None) -> iter:
        model = model or self.default_model
        if not usable_key(self._api_key):
            raise ProviderError("GEMINI_API_KEY not configured", "gemini")
        url = f"{get_settings().gemini_api_base}/{model}:streamGenerateContent?alt=sse"
        try:
            for attempt in range(2):
                payload = self._payload(messages, model)
                with httpx.stream(
                    "POST", url, json=payload, headers={"x-goog-api-key": self._api_key}, timeout=get_settings().llm_timeout_seconds
                ) as resp:
                    if resp.status_code != 200:
                        resp.read()
                        if attempt == 0 and "generationConfig" in payload and _rejects_thinking_level(resp):
                            logger.info("%s rejects thinking level %r; using its default.", model, self.thinking_level)
                            _NO_THINKING_LEVEL.add(model)
                            continue
                        raise ProviderError(f"gemini http {resp.status_code} ({model}): {_error_detail(resp)}", "gemini")
                    yield from self._stream_text(resp)
                    return
        except httpx.HTTPError as exc:
            raise ProviderError(f"gemini transport: {exc}", "gemini") from exc

    @staticmethod
    def _stream_text(resp: httpx.Response):
        for line in resp.iter_lines():
            if not line.startswith("data:"):
                continue
            try:
                chunk = json.loads(line[5:].strip())
                parts = chunk["candidates"][0]["content"]["parts"]
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
            text = _answer_text(parts)
            if text:
                yield text

    def complete(self, messages, model=None, *, json_mode=False) -> str:
        model = model or self.default_model
        if not usable_key(self._api_key):
            raise ProviderError("GEMINI_API_KEY not configured", "gemini")
        url = f"{get_settings().gemini_api_base}/{model}:generateContent"
        try:
            payload = self._payload(messages, model, json_mode=json_mode)
            resp = httpx.post(url, json=payload, headers={"x-goog-api-key": self._api_key}, timeout=get_settings().llm_timeout_seconds)
            if _rejects_thinking_level(resp) and "thinkingConfig" in payload.get("generationConfig", {}):
                _NO_THINKING_LEVEL.add(model)
                payload = self._payload(messages, model, json_mode=json_mode)
                resp = httpx.post(url, json=payload, headers={"x-goog-api-key": self._api_key}, timeout=get_settings().llm_timeout_seconds)
            if resp.status_code != 200:
                raise ProviderError(f"gemini http {resp.status_code} ({model}): {_error_detail(resp)}", "gemini")
            parts = resp.json()["candidates"][0]["content"]["parts"]
            return _answer_text(parts)
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            raise ProviderError(f"gemini complete failed: {exc}", "gemini") from exc
