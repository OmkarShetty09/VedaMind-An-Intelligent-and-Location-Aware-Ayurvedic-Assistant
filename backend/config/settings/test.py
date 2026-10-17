"""Test settings: Celery runs synchronously, DB uses test database."""

from .dev import *  # noqa: F403

# Celery: run tasks synchronously in tests (no broker needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use test database (pytest-django handles this automatically)
# But ensure we don't connect to production Redis
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# Throttle counters and the consent flag live in the cache; keep tests independent of Redis.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Tests make many anonymous auth calls in a few seconds; production limits would trip them.
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/min",
    "authed": "1000/min",
    "chat": "1000/min",
    "guardrail": "1000/min",
}

# A real-length key: PyJWT warns on short HMAC keys such as the "change-me" placeholder.
SIMPLE_JWT = {**SIMPLE_JWT, "SIGNING_KEY": "test-signing-key-0123456789abcdef0123456789abcdef"}  # noqa: F405
