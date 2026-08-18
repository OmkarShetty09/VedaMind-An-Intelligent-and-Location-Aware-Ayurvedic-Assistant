from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.core.middleware.health_check import healthz


def index(_request):
    return JsonResponse({"service": "vedamind-backend", "status": "ok"})


urlpatterns = [
    path("", index, name="index"),
    path("healthz", healthz, name="healthz"),
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/users/", include("apps.users.user_urls")),
    path("api/v1/dosha/", include("apps.dosha_profiles.urls")),
    path("api/v1/guardrails/", include("apps.guardrails.urls")),
    path("api/v1/interactions-log/", include("apps.interactions_log.urls")),
    path("api/v1/chat/", include("apps.conversations.urls")),
    path("api/v1/dinacharya/", include("apps.dinacharya.urls")),
    path("api/v1/weather/", include("apps.weather.urls")),
]
