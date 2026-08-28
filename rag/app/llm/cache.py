"""Identical-query cache: normalized query + context ids + prompt/model version."""

import hashlib
import json

import redis

from app.config import get_settings

_cache: redis.Redis | None = None


def _redis():
    global _cache
    if _cache is None:
        _cache = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)
    return _cache


def cache_key(query: str, context_ids: list[str], prompt_version: str, model: str) -> str:
    blob = json.dumps([query.lower().strip(), sorted(context_ids), prompt_version, model], sort_keys=True)
    return "rag:q:" + hashlib.sha256(blob.encode()).hexdigest()


def get_cached(key: str):
    try:
        value = _redis().get(key)
        return json.loads(value) if value else None
    except (redis.RedisError, json.JSONDecodeError):
        return None


def set_cached(key: str, payload: dict, ttl_hours: int) -> None:
    try:
        _redis().set(key, json.dumps(payload), ex=ttl_hours * 3600)
    except redis.RedisError:
        pass


def reset_cache() -> None:
    """Reset the singleton Redis connection (for test isolation)."""
    global _cache
    _cache = None