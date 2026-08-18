from django.conf import settings
from django.db import models


class OwnershipMixin(models.Model):
    """Restrict objects to their owner: user FK + enforced scoping."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s"
    )

    class Meta:
        abstract = True


class AuditableMixin(models.Model):
    """Append-only invariant: this model must never be updated or deleted."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk and self._state.adding is False and hasattr(self, "_audit_immutable") and self._audit_immutable:
            raise NotImplementedError("Audit records are append-only; create a new row with supersedes.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # pragma: no cover - invariant enforced by DB too
        raise NotImplementedError("Audit records are append-only and cannot be deleted.")
