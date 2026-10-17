from .openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq LLM provider via its OpenAI-compatible endpoint (URL from settings.groq_chat_url)."""

    name = "groq"
