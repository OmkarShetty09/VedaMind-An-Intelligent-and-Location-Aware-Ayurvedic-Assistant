from ._checks import require_strong_secrets
from .base import *  # noqa: F403
from .base import RAG_ADMIN_TOKEN, SECRET_KEY, SIMPLE_JWT, env

DEBUG = False
# No default domains: a deployment must say where it is served from.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
REFRESH_COOKIE_SECURE = True
LOGGING["root"]["level"] = "INFO"  # noqa: F405

require_strong_secrets(
    DJANGO_SECRET_KEY=SECRET_KEY, JWT_SIGNING_KEY=SIMPLE_JWT["SIGNING_KEY"], RAG_ADMIN_TOKEN=RAG_ADMIN_TOKEN
)
