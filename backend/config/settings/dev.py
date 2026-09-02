from .base import *  # noqa: F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# Keep console logging plain + verbose for DX.
LOGGING["formatters"]["plain"]["format"] = "%(asctime)s %(levelname)s %(name)s %(message)s"  # noqa: F405
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405

# Weather: Open-Meteo requires no API key.
env.read_env(BASE_DIR.parent / ".env")  # noqa: F405
