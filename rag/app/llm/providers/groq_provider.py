from .openai_provider import OpenAIProvider

_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(OpenAIProvider):
    """Groq LLM provider via its OpenAI-compatible endpoint."""

    name = "groq"
    base_url = _URL