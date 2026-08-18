from django.contrib import admin

from .models import ConsentRecord, GuardrailDecision


@admin.register(GuardrailDecision)
class GuardrailDecisionAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "decision", "severity", "reason_code", "engine_version"]
    list_filter = ["decision", "severity", "reason_code"]
    readonly_fields = ["entities", "matched_rules", "input_snippet", "correlation_id"]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):  # append-only in the admin too
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "disclaimer_version"]
    readonly_fields = ["ip_hash"]

    def has_change_permission(self, request, obj=None):
        return False
