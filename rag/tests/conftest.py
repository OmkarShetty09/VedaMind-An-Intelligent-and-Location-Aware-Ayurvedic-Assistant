"""Test environment: no real keys, no network, fail fast on external calls."""

import pytest


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch):
    """Set safe env defaults and restore original state after each test."""
    defaults = {
        "VECTOR_STORE": "pgvector",
        "RAG_ADMIN_TOKEN": "test-token",
        "OPENAI_API_KEY": "",
        "GEMINI_API_KEY": "",
        "GROQ_API_KEY": "",
        "OLLAMA_BASE_URL": "http://localhost:11434/v1",
        "DATABASE_URL": "postgresql://x:x@localhost:5432/nope",
        "REDIS_URL": "redis://localhost:6399/0",
        "RERANKER_ENABLED": "false",
        "BACKEND_GUARDRAIL_URL": "http://backend.test/check",
    }
    for key, value in defaults.items():
        monkeypatch.setenv(key, value)

    from app.config import get_settings
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset all module-level singletons before each test."""
    from app.llm import cache as llm_cache
    from app.llm import token_budget
    from app.retrieval import deps_store, reranker

    deps_store.reset_store()
    llm_cache.reset_cache()
    token_budget.reset_cache()
    reranker.reset_reranker()

    yield

    deps_store.reset_store()
    llm_cache.reset_cache()
    token_budget.reset_cache()
    reranker.reset_reranker()
