from .base import *  # noqa: F403
from .base import env

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["api.vedamind.app"])
REFRESH_COOKIE_SECURE = True
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["https://vedamind.app"])
LOGGING["root"]["level"] = "INFO"  # noqa: F405
