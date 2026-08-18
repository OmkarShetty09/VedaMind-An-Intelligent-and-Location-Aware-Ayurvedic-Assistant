from rest_framework import generics, permissions
from rest_framework.permissions import BasePermission

from .models import GuardrailDecision
from .serializers import GuardrailDecisionSerializer


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class AuditLogListView(generics.ListAPIView):
    """GET /api/v1/interactions-log - staff-only query of guardrail decisions."""

    serializer_class = GuardrailDecisionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]
    search_fields = ["entities", "matched_rules"]

    def get_queryset(self):
        return GuardrailDecision.objects.select_related("user").all()
