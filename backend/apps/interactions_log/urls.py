from django.urls import path

from .views import AuditLogListView

urlpatterns = [
    path("", AuditLogListView.as_view(), name="interactions-log-list"),
]
