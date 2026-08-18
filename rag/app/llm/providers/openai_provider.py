import json
import logging

import httpx

from app.core.errors import ProviderError

from .base import LLMProvider

logger = logging.getLogger("rag.llm.openai")

_URL = "https://api.openai.com/v1/chat/completions"
_TIMEOUT = 60.0


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, default_model: str):
        self._api_key = api_key
        self.default_model = default_model

    def generate(self, messages, model=None) -> iter:
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            with httpx.stream("POST", _URL, json=payload, headers=headers, timeout=_TIMEOUT) as resp:
                if resp.status_code != 200:
                    raise ProviderError(f"openai http {resp.status_code}", "openai")
                for line in resp.iter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content")
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                    if delta:
                        yield delta
        except httpx.HTTPError as exc:
            raise ProviderError(f"openai transport: {exc}", "openai") from exc

    def complete(self, messages, model=None, *, json_mode=False) -> str:
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": 0.0,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            resp = httpx.post(_URL, json=payload, headers=headers, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderError(f"openai complete failed: {exc}", "openai") from exc