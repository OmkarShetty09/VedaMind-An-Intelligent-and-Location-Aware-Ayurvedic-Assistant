"""Base settings shared by dev/staging/prod. Everything is env-driven."""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR.parent / ".env")

# Required: no secret has a fallback in code (setup.ps1 generates random values into .env).
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    # local
    "apps.core",
    "apps.users",
    "apps.dosha_profiles",
    "apps.guardrails",
    "apps.interactions_log",
    "apps.conversations",
    "apps.dinacharya",
    "apps.weather",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.request_context.RequestContextMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="vedamind"),
        "USER": env("POSTGRES_USER", default="vedamind"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="vedamind"),
        "HOST": env("POSTGRES_HOST", default="127.0.0.1"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
        "CONN_MAX_AGE": 60,
    }
}
# infra/docker-compose.prod.yml passes a single DATABASE_URL; it wins over POSTGRES_* when set.
if env("DATABASE_URL", default=""):
    DATABASES["default"] = env.db("DATABASE_URL")
    DATABASES["default"]["CONN_MAX_AGE"] = 60

AUTH_USER_MODEL = "users.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- REST framework ----
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # Chat and guardrail views add their own scoped throttles (see apps.core.throttling).
    "DEFAULT_THROTTLE_CLASSES": (
        "apps.core.throttling.AnonRateThrottle",
        "apps.core.throttling.AuthedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("THROTTLE_ANON", default="30/min"),
        "authed": env("THROTTLE_AUTHED", default="120/min"),
        "chat": env("THROTTLE_CHAT", default="20/min"),
        "guardrail": env("THROTTLE_GUARDRAIL", default="60/min"),
    },
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.CursorPagination",
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
    "UNAUTHENTICATED_USER": None,
}

# ---- JWT (rotating refresh + blacklist via token_blacklist) ----
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("ACCESS_TOKEN_MINUTES", default=15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("REFRESH_TOKEN_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---- Cookies for refresh token ----
REFRESH_COOKIE_NAME = "vedamind_refresh"
REFRESH_COOKIE_HTTPONLY = True
REFRESH_COOKIE_SAMESITE = "Strict"
REFRESH_COOKIE_SECURE = not DEBUG
REFRESH_COOKIE_PATH = "/api/v1/auth/"

# ---- CORS ----
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:5173"])
CORS_ALLOW_CREDENTIALS = True

# ---- Redis / cache ----
REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# ---- Celery ----
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# ---- RAG service ----
RAG_SERVICE_URL = env("RAG_SERVICE_URL", default="http://127.0.0.1:8001")
RAG_ADMIN_TOKEN = env("RAG_ADMIN_TOKEN")

# ---- Weather / geocoding (Open-Meteo + OpenStreetMap Nominatim, no API keys) ----
WEATHER_CACHE_TTL_MINUTES = env.int("WEATHER_CACHE_TTL_MINUTES", default=30)
OPEN_METEO_FORECAST_URL = env("OPEN_METEO_FORECAST_URL", default="https://api.open-meteo.com/v1/forecast")
OPEN_METEO_GEOCODING_URL = env("OPEN_METEO_GEOCODING_URL", default="https://geocoding-api.open-meteo.com/v1/search")
NOMINATIM_REVERSE_URL = env("NOMINATIM_REVERSE_URL", default="https://nominatim.openstreetmap.org/reverse")
# Nominatim's usage policy requires an identifying User-Agent.
GEOCODER_USER_AGENT = env("GEOCODER_USER_AGENT", default="VedaMind/1.0 (student project)")
EXTERNAL_HTTP_TIMEOUT_SECONDS = env.float("EXTERNAL_HTTP_TIMEOUT_SECONDS", default=5.0)

# Dosha used for routines before the user has taken the quiz.
DINACHARYA_DEFAULT_DOSHA = env("DINACHARYA_DEFAULT_DOSHA", default="vata")

# ---- Accounts created by `seed_demo_data` / `create_superuser` (skipped when unset) ----
ADMIN_EMAIL = env("DEMO_EMAIL", default="")
ADMIN_PASSWORD = env("DEMO_PASSWORD", default="")
DEMO_USER_EMAIL = env("DEMO_USER_EMAIL", default="")
DEMO_USER_PASSWORD = env("DEMO_USER_PASSWORD", default="")

# ---- Guardrail audit digest (Celery beat) ----
GUARDRAIL_DIGEST_RECIPIENTS = env.list("GUARDRAIL_DIGEST_RECIPIENTS", default=[])
GUARDRAIL_RULE_STEWARD = env("GUARDRAIL_RULE_STEWARD", default="unassigned")
CELERY_BEAT_SCHEDULE = {
    "weather-refresh-sweep": {
        "task": "apps.weather.tasks.refresh_weather_sweep",
        "schedule": env.float("WEATHER_REFRESH_SECONDS", default=3600.0),
    },
    "guardrail-daily-digest": {
        "task": "apps.interactions_log.tasks.daily_digest",
        "schedule": env.float("GUARDRAIL_DIGEST_SECONDS", default=86400.0),
    },
}

# ---- Logging (JSON in prod, structured) ----
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "pythonjsonlogger.json.JsonFormatter", "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s"},
        "plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json" if not DEBUG else "plain"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "apps.guardrails": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "apps.interactions_log": {"level": "INFO", "handlers": ["console"], "propagate": False},
    },
}
