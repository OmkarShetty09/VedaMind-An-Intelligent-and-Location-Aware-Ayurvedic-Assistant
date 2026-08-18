import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel

DOSHAS = ("vata", "pitta", "kapha")


class DoshaProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dosha_profile")
    prakriti_scores = models.JSONField(default=dict)  # {vata: 0..100, pitta: .., kapha: ..}
    vikriti_scores = models.JSONField(default=dict)
    dominant_dosha = models.CharField(max_length=10, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id}: {self.dominant_dosha or 'unscored'}"


class DoshaAssessment(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dosha_assessments")
    quiz_version = models.CharField(max_length=16, default="1.0")
    answers = models.JSONField(default=dict)
    results = models.JSONField(default=dict)  # computed scores + dominant dosha

    def __str__(self):
        return f"{self.user_id}: {self.quiz_version} @ {self.created_at.isoformat()}"
