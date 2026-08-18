import uuid

from django.conf import settings
from django.db import models

SEASONS = ("vasant", "grishma", "varsha", "sharad", "hemant", "shishir")


class DinacharyaRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dinacharya_recs")
    date = models.DateField(db_index=True)
    season = models.CharField(max_length=16, choices=[(s, s) for s in SEASONS])
    engine_version = models.CharField(max_length=16, default="1.0.0")
    inputs_snapshot = models.JSONField(default=dict)  # kala, weather, dosha flags at generation time
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user_id}: {self.date} ({self.season})"


class RoutineActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommendation = models.ForeignKey(DinacharyaRecommendation, on_delete=models.CASCADE, related_name="activities")
    time_of_day = models.CharField(max_length=32)
    start = models.TimeField()
    end = models.TimeField(null=True, blank=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    reasons = models.JSONField(default=list)
    citations = models.JSONField(default=list)  # [{"source": ..., "ref": ...}]
    dosha_target = models.CharField(max_length=10, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "start"]

    def __str__(self):
        return f"{self.start:%H:%M} {self.title}"
