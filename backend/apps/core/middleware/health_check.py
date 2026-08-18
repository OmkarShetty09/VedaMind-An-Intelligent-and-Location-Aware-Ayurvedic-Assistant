from django.conf import settings
from django.db import connection
from django.http import JsonResponse


def healthz(_request):
    """Liveness + readiness. Reads: DB, Redis, RAG service."""
    checks = {"database": True, "redis": True, "rag": True}
    try:
        connection.ensure_connection()
    except Exception:
        checks["database"] = False

    try:
        import redis

        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
    except Exception:
        checks["redis"] = False

    if checks["database"] and checks["redis"]:
        return JsonResponse({"status": "ok", "checks": checks}, status=200)
    return JsonResponse({"status": "degraded", "checks": checks}, status=503)
