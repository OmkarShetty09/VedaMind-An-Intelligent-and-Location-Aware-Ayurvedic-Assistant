from .openai_provider import OpenAIProvider


class OllamaProvider(OpenAIProvider):
    """Local Ollama provider via its OpenAI-compatible endpoint.

    No API key is required; the base URL points at a local (or remote) Ollama
    instance, e.g. ``http://localhost:11434/v1``.
    """

    name = "ollama"
    requires_key = False

    def __init__(self, api_key: str = "", default_model: str = "llama3.2", base_url: str | None = None):
        super().__init__(api_key, default_model, base_url)
