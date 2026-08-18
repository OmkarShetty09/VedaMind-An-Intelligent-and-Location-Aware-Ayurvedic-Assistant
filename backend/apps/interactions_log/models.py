import uuid

from django.conf import settings
from django.db import models, transaction

from apps.core.mixins import AuditableMixin


class GuardrailDecision(AuditableMixin, models.Model):
    """Append-only record of every safety decision. Insert-only at the DB layer.

    Corrections write a new row with `supersedes`; never an update.
    """

    _audit_immutable = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    conversation = models.ForeignKey(
        "conversations.Conversation", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    message = models.ForeignKey("conversations.Message", on_delete=models.SET_NULL, null=True, related_name="+")
    correlation_id = models.CharField(max_length=64, blank=True)

    entities = models.JSONField(default=dict)  # {herbs: [], drugs: [], ambiguous: []}
    matched_rules = models.JSONField(default=list)
    severity = models.CharField(max_length=16, default="none")
    decision = models.CharField(max_length=16)
    reason_code = models.CharField(max_length=48)
    engine_version = models.CharField(max_length=32, blank=True)
    llm_version = models.CharField(max_length=64, blank=True)
    input_snippet = models.TextField(blank=True)  # redacted

    supersedes = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.decision}:{self.reason_code} ({self.user_id})"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            return super().save(*args, **kwargs)


class ConsentRecord(AuditableMixin, models.Model):
    """Informed-consent acceptance. Append-only for legal review."""

    _audit_immutable = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consents")
    disclaimer_version = models.CharField(max_length=20)
    ip_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"consent v{self.disclaimer_version} ({self.user_id})"
