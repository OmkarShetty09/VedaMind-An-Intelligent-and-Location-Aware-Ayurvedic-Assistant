import json
import logging

import httpx

from app.config import get_settings, usable_key
from app.core.errors import ProviderError

from .base import LLMProvider

logger = logging.getLogger("rag.llm.openai")



class OpenAIProvider(LLMProvider):
    """OpenAI-compatible chat provider (OpenAI, Groq, Ollama, etc.).

    Any service exposing the OpenAI ``/chat/completions`` surface can be used by
    subclassing and overriding ``name`` and ``base_url``.
    """

    name = "openai"
    base_url = ""  # set from settings by the router
    requires_key = True

    def __init__(self, api_key: str, default_model: str, base_url: str | None = None):
        self._api_key = api_key
        self.default_model = default_model
        if base_url:
            # Accept either the API root (".../v1", as in OLLAMA_BASE_URL) or the full endpoint.
            base_url = base_url.rstrip("/")
            if not base_url.endswith("/chat/completions"):
                base_url += "/chat/completions"
            self.base_url = base_url

    def _check_configured(self):
        if self.requires_key and not usable_key(self._api_key):
            raise ProviderError("API key not configured", self.name)

    def generate(self, messages, model=None) -> iter:
        model = model or self.default_model
        self._check_configured()
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            with httpx.stream("POST", self.base_url, json=payload, headers=headers, timeout=get_settings().llm_timeout_seconds) as resp:
                if resp.status_code != 200:
                    resp.read()
                    raise ProviderError(f"{self.name} http {resp.status_code} ({model}): {resp.text[:300]}", self.name)
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
            raise ProviderError(f"{self.name} transport: {exc}", self.name) from exc

    def complete(self, messages, model=None, *, json_mode=False) -> str:
        model = model or self.default_model
        self._check_configured()
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
            resp = httpx.post(self.base_url, json=payload, headers=headers, timeout=get_settings().llm_timeout_seconds)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderError(f"{self.name} complete failed: {exc}", self.name) from exc