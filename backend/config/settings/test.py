"""Test settings: Celery runs synchronously, DB uses test database."""

from .dev import *  # noqa: F403

# Celery: run tasks synchronously in tests (no broker needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use test database (pytest-django handles this automatically)
# But ensure we don't connect to production Redis
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
