from django.db import models

from .severity import Evidence, Severity


class RuleVersion(models.Model):
    """An immutable snapshot of the ruleset, stamped by the clinician steward."""

    version = models.CharField(max_length=32, unique=True)
    sha256 = models.CharField(max_length=64)
    activated_at = models.DateTimeField(auto_now_add=True)
    steward = models.CharField(max_length=120)

    def __str__(self):
        return self.version


class InteractionRule(models.Model):
    """One curated herb-drug / herb-herb / context interaction.

    Safety contract: a rule cannot be saved without severity, evidence and a
    citation (source_uri), so nothing enters the engine unproven.
    """

    herb_a = models.CharField(max_length=120, db_index=True)  # canonical herb name
    herb_b_or_drug = models.CharField(max_length=120, blank=True)  # drug/substance or second herb
    direction = models.CharField(
        max_length=16,
        choices=[("herb_drug", "herb_drug"), ("herb_herb", "herb_herb")],
        default="herb_drug",
    )
    interaction_type = models.CharField(max_length=64, blank=True)  # e.g. antiplatelet, hypokalemia
    mechanism = models.TextField(blank=True)
    recommendation = models.TextField()  # user-facing guidance
    severity = models.CharField(max_length=16, choices=[(s.name, s.name) for s in Severity])
    evidence = models.CharField(max_length=16, choices=[(e.name, e.name) for e in Evidence])
    dose_threshold = models.CharField(max_length=64, blank=True)  # empty = dose-independent
    context_tag = models.CharField(
        max_length=32,
        choices=[("", "any"), ("pregnancy", "pregnancy"), ("pediatric", "pediatric (<12y)"),
                 ("renal", "renal impairment"), ("diabetes", "diabetes")],
        default="",
        blank=True,
    )
    source_uri = models.URLField()
    active = models.BooleanField(default=True)
    rule_version = models.ForeignKey(RuleVersion, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["herb_a", "herb_b_or_drug"])]

    def __str__(self):
        return f"{self.herb_a} <-> {self.herb_b_or_drug or self.context_tag} [{self.severity}/{self.evidence}]"


class HerbAlias(models.Model):
    """Name resolution: sanskrit / latin / common / hindi -> canonical herb."""

    canonical_herb = models.CharField(max_length=120, db_index=True)
    alias = models.CharField(max_length=120, db_index=True)
    language = models.CharField(max_length=16, default="common")
    confidence = models.FloatField(default=1.0)

    class Meta:
        unique_together = ("canonical_herb", "alias")

    def __str__(self):
        return f"{self.alias} -> {self.canonical_herb}"
