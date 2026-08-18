from .base import *  # noqa: F403
from .base import env

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["staging.vedamind.app"])
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
