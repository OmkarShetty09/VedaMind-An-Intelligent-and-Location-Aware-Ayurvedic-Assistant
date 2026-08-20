"""Test environment: no real keys, no network, fail fast on external calls."""

import os

os.environ.setdefault("VECTOR_STORE", "pgvector")
os.environ.setdefault("RAG_ADMIN_TOKEN", "test-token")
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434/v1")
os.environ.setdefault("DATABASE_URL", "postgresql://x:x@localhost:5432/nope")
os.environ.setdefault("REDIS_URL", "redis://localhost:6399/0")
os.environ.setdefault("RERANKER_ENABLED", "false")
os.environ.setdefault("BACKEND_GUARDRAIL_URL", "http://backend.test/check")

from app.config import get_settings

get_settings.cache_clear()