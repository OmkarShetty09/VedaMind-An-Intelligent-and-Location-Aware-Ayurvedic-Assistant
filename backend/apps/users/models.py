import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from apps.core.models import TimestampedModel
from apps.core.validators import validate_timezone

from .managers import UserManager


class User(AbstractBaseUser, TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120)
    timezone = models.CharField(max_length=64, default="UTC", validators=[validate_timezone])

    consent_accepted = models.BooleanField(default=False)
    consent_version = models.CharField(max_length=20, default="1.0")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):  # admin compatibility
        return self.is_superuser

    def has_module_perms(self, app_label):  # admin compatibility
        return self.is_staff


class UserMedication(models.Model):
    """Self-reported medication - feeds the guardrail entity extraction."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medications")
    free_text = models.CharField(max_length=255)
    canonical_drug_ids = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.free_text} ({self.user_id})"


class UserCondition(models.Model):
    """Self-reported conditions (e.g. pregnancy, diabetes) - guardrail context."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conditions")
    condition = models.CharField(max_length=120)
    severity = models.CharField(max_length=20, default="unknown")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.condition} ({self.user_id})"
