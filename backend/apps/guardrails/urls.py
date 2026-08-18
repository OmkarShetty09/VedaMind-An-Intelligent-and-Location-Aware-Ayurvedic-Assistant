from django.urls import path

from .views import InteractionCheckView, KnownInteractionsView

urlpatterns = [
    path("check", InteractionCheckView.as_view(), name="guardrails-check"),
    path("interactions/<str:herb>", KnownInteractionsView.as_view(), name="guardrails-known"),
]
