import json
import logging

import httpx

from app.core.errors import ProviderError

from .base import LLMProvider

logger = logging.getLogger("rag.llm.gemini")

_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
_TIMEOUT = 60.0


def _to_gemini_messages(messages: list[dict]) -> list[dict]:
    return [{"role": "model" if m["role"] == "assistant" else m["role"], "parts": [{"text": m["content"]}]} for m in messages]


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, default_model: str):
        self._api_key = api_key
        self.default_model = default_model

    def generate(self, messages, model=None) -> iter:
        model = model or self.default_model
        url = f"{_BASE}/{model}:streamGenerateContent?alt=sse"
        payload = {"contents": _to_gemini_messages(messages)}
        try:
            with httpx.stream("POST", url, json=payload, headers={"x-goog-api-key": self._api_key}, timeout=_TIMEOUT) as resp:
                if resp.status_code != 200:
                    raise ProviderError(f"gemini http {resp.status_code}", "gemini")
                for line in resp.iter_lines():
                    if not line.startswith("data:"):
                        continue
                    try:
                        chunk = json.loads(line[5:].strip())
                        parts = chunk["candidates"][0]["content"]["parts"]
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                    for part in parts:
                        text = part.get("text", "")
                        if text:
                            yield text
        except httpx.HTTPError as exc:
            raise ProviderError(f"gemini transport: {exc}", "gemini") from exc

    def complete(self, messages, model=None, *, json_mode=False) -> str:
        model = model or self.default_model
        url = f"{_BASE}/{model}:generateContent"
        payload = {"contents": _to_gemini_messages(messages)}
        if json_mode:
            payload["generationConfig"] = {"responseMimeType": "application/json"}
        try:
            resp = httpx.post(url, json=payload, headers={"x-goog-api-key": self._api_key}, timeout=_TIMEOUT)
            resp.raise_for_status()
            parts = resp.json()["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderError(f"gemini complete failed: {exc}", "gemini") from exc