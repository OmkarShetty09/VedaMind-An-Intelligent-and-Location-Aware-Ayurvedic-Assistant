"""Token budgeting: per-request context cap + per-user daily cap via Redis."""

import redis

from app.config import get_settings

_cache: redis.Redis | None = None


def _redis():
    global _cache
    if _cache is None:
        _cache = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)
    return _cache


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def enforce_context_budget(assembled: list[dict], max_tokens: int) -> list[dict]:
    """Drop lowest-priority passages first, never mid-shloka (chunks are atomic)."""
    budget = max_tokens
    kept: list[dict] = []
    for item in assembled:  # items arrive relevance-ordered
        cost = estimate_tokens(item["content"])
        if cost > budget:
            break
        kept.append(item)
        budget -= cost
    return kept


def check_daily_budget(user_id: str, extra_tokens: int) -> bool:
    key = f"rag:budget:{user_id}"
    try:
        used = _redis().incrby(key, extra_tokens)
        if used == extra_tokens:
            _redis().expire(key, 86400)
        return used <= get_settings().daily_token_budget
    except redis.RedisError:
        return True  # budget service down -> allow (logged upstream); safety decided by guardrails, not budget


def reset_cache() -> None:
    """Reset the singleton Redis connection (for test isolation)."""
    global _cache
    _cache = None