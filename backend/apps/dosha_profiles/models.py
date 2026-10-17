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
    secondary_dosha = models.CharField(max_length=10, blank=True, default="")
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


class DoshaInfo(models.Model):
    """Display content for each dosha (result screen). Edited in the admin."""

    dosha = models.CharField(max_length=10, unique=True, choices=[(d, d) for d in DOSHAS])
    label = models.CharField(max_length=40)
    element = models.CharField(max_length=60)
    tagline = models.CharField(max_length=120)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "dosha info"

    def __str__(self):
        return self.label


class QuizQuestion(models.Model):
    """One Prakriti quiz question. `options` = [{"text": ..., "dosha": "vata"|"pitta"|"kapha"}, ...]."""

    key = models.SlugField(max_length=60, unique=True)
    section = models.CharField(max_length=80)
    prompt = models.CharField(max_length=200)
    options = models.JSONField(default=list)
    order = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.order}. {self.prompt}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if len(self.options) < 2 or any(o.get("dosha") not in DOSHAS or not o.get("text") for o in self.options):
            raise ValidationError(
                {"options": 'Give at least two options, each {"text": ..., "dosha": vata|pitta|kapha}.'}
            )
