import uuid

from django.conf import settings
from django.db import models

from .ritu import seasons as _ritu_seasons

# One calendar for the whole app: data/ritu.json.
SEASONS = tuple(s["key"] for s in _ritu_seasons())


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
    personalized = models.BooleanField(default=False)  # changed or added because of the user's dosha
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "start"]

    def __str__(self):
        return f"{self.start:%H:%M} {self.title}"


class RoutineTemplate(models.Model):
    """One Dinacharya activity rule, rendered per user by engine.build_routine(). Edited in the admin.

    start / end: {"anchor": "sunrise"|"sunset"|"clock", "offset_minutes": int, "clock": "HH:MM",
                  "fallback_clock": "HH:MM" (used for sun anchors when the location is unknown)}
    Text may contain {dosha} / {secondary}. season_overrides / dosha_overrides map a season / the user's
    dominant dosha to fields to replace (e.g. a different oil in winter, dry massage for kapha).
    dosha_tips adds a dosha-specific reason for the dominant and secondary dosha; doshas limits the
    activity to users whose dominant or secondary dosha is listed (empty = everyone).
    """

    key = models.SlugField(max_length=60, unique=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Tie-breaker when two activities start together.")
    active = models.BooleanField(default=True)
    time_of_day = models.CharField(max_length=32)
    start = models.JSONField()
    end = models.JSONField(null=True, blank=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    reasons = models.JSONField(default=list, blank=True)
    citations = models.JSONField(default=list, blank=True)
    dosha_target = models.CharField(max_length=10, blank=True)
    above_temperature_c = models.FloatField(
        null=True, blank=True, help_text="Only include the activity when it is hotter than this."
    )
    season_overrides = models.JSONField(default=dict, blank=True)
    dosha_overrides = models.JSONField(default=dict, blank=True)
    dosha_tips = models.JSONField(default=dict, blank=True)
    doshas = models.JSONField(default=list, blank=True, help_text='Only for these doshas, e.g. ["kapha"]. Empty = all.')

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title

    def as_dict(self) -> dict:
        fields = ("key", "order", "time_of_day", "start", "end", "title", "description", "reasons", "citations",
                  "dosha_target", "above_temperature_c", "season_overrides", "dosha_overrides", "dosha_tips", "doshas")
        return {f: getattr(self, f) for f in fields}
