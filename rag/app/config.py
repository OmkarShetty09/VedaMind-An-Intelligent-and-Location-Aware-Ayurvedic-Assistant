from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    env: str = "dev"

    database_url: str = "postgresql://vedamind:vedamind@localhost:5432/vedamind"
    redis_url: str = "redis://localhost:6379/0"

    rag_admin_token: str = "dev-token"
    backend_guardrail_url: str = "http://localhost:8000/api/v1/guardrails/check"

    vector_store: str = "pgvector"  # pgvector | milvus

    embedding_model: str = "text-embedding-3-large"
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
    ollama_base_url: str = "http://localhost:11434/v1"
    llm_primary_model: str = "gemini-2.0-flash"  # primary generator
    llm_fallback_model: str = "llama-3.3-70b-versatile"  # live fallback (Groq)
    llm_local_fallback_model: str = "llama3.2"  # offline fallback (Ollama)
    llm_cheap_model: str = "gemini-2.0-flash"  # extraction / summarization / judging

    daily_token_budget: int = 200_000

    chunk_overlap: int = 100
    chunk_size: int = 500


@lru_cache
def get_settings() -> Settings:
    return Settings()