from .base import *  # noqa: F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:5173", "http://127.0.0.1:5173"])

# base.py derives this from the DEBUG env var; dev always runs over plain http.
REFRESH_COOKIE_SECURE = False

# runserver serves static files itself; WhiteNoise would only warn that STATIC_ROOT (collectstatic) is missing.
MIDDLEWARE = [m for m in MIDDLEWARE if m != "whitenoise.middleware.WhiteNoiseMiddleware"]  # noqa: F405

# Keep console logging plain + verbose for DX.
LOGGING["formatters"]["plain"]["format"] = "%(asctime)s %(levelname)s %(name)s %(message)s"  # noqa: F405
LOGGING["handlers"]["console"]["formatter"] = "plain"  # noqa: F405
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
# Per-query SQL and HTTP-client wire logs drown out the useful lines at DEBUG.
for _noisy in ("django.db.backends", "django.utils.autoreload", "httpcore", "httpx", "urllib3"):
    LOGGING["loggers"][_noisy] = {"level": "INFO"}  # noqa: F405

# Weather: Open-Meteo requires no API key.
env.read_env(BASE_DIR.parent / ".env")  # noqa: F405
