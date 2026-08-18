import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title or 'Conversation'} ({self.user_id})"


class Message(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=16, choices=[("user", "user"), ("assistant", "assistant"), ("system", "system")])
    content = models.TextField(null=True, blank=True)  # noqa: DJ001 - null marks guardrail-blocked turns
    source_citations = models.JSONField(default=list)
    guardrail_decision = models.ForeignKey(
        "interactions_log.GuardrailDecision", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    llm_model = models.CharField(max_length=64, blank=True)
    tokens = models.PositiveIntegerField(default=0)
    block_reason = models.CharField(max_length=48, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}:{self.content[:32] if self.content else '(blocked)'}"
