from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The shared .env lives at the repo root; resolve it from this file so the
# service reads it no matter which directory uvicorn / the CLI is started from.
_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(_ROOT_ENV, ".env"), extra="ignore")

    env: str = "dev"

    database_url: str = "postgresql://vedamind:vedamind@127.0.0.1:5432/vedamind"
    redis_url: str = "redis://127.0.0.1:6379/0"

    rag_admin_token: str  # required: shared secret with the backend (no default in code)
    backend_guardrail_url: str = "http://127.0.0.1:8000/api/v1/guardrails/check"

    vector_store: str = "pgvector"  # pgvector | milvus
    milvus_uri: str = "http://milvus:19530"  # only used when VECTOR_STORE=milvus

    embedding_model: str = "text-embedding-3-large"  # OpenAI embedding model (used only without a Gemini key)
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dim: int = 1024
    reranker_model: str = "bge-reranker-v2-m3"
    reranker_enabled: bool = False  # requires sentence-transformers installed

    retrieval_top_k: int = 8
    retrieval_candidates: int = 50
    context_max_tokens: int = 6000
    query_cache_ttl_hours: int = 24

    openai_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    ollama_base_url: str = "http://127.0.0.1:11434/v1"
    gemini_api_base: str = "https://generativelanguage.googleapis.com/v1beta/models"
    groq_chat_url: str = "https://api.groq.com/openai/v1/chat/completions"
    openai_chat_url: str = "https://api.openai.com/v1/chat/completions"
    openai_embeddings_url: str = "https://api.openai.com/v1/embeddings"
    # gemini-2.0-flash was shut down on 2026-06-01; these are current free-tier models.
    llm_primary_model: str = "gemini-3.6-flash"  # primary generator
    llm_fallback_model: str = "openai/gpt-oss-120b"  # live fallback (Groq production model)
    llm_local_fallback_model: str = "llama3.2"  # offline fallback (Ollama)
    llm_cheap_model: str = "gemini-3.5-flash-lite"  # extraction / summarization / judging
    # Gemini 3 "thinking" before the first token: minimal ~1.5s, default (medium) 6-10s. Empty = model default.
    llm_thinking_level: str = "minimal"

    daily_token_budget: int = 200_000
    llm_timeout_seconds: float = 60.0
    guardrail_timeout_seconds: float = 15.0

    # Corpus root (raw/ sources, processed/ chunks + manifest). Default: <repo>/data.
    data_dir: Path = Path(__file__).resolve().parents[2] / "data"

    chunk_overlap: int = 100
    chunk_size: int = 500


def usable_key(key: str | None) -> bool:
    """False for empty values and the placeholders shipped in .env.example."""
    key = (key or "").strip()
    if len(key) <= 10 or key.endswith("...") or key.lower().startswith(("your-", "your_", "change-me", "sk-...")):
        return False
    return True


@lru_cache
def get_settings() -> Settings:
    return Settings()
