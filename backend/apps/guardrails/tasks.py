import hashlib
import json

from celery import shared_task

from .models import InteractionRule, RuleVersion


@shared_task
def activate_rule_version(version: str, steward: str):
    """Freeze the active ruleset into a versioned, sha256-pinned snapshot."""
    rules = InteractionRule.objects.filter(active=True).order_by("id")
    payload = json.dumps(
        [
            {
                "herb_a": r.herb_a,
                "herb_b_or_drug": r.herb_b_or_drug,
                "severity": r.severity,
                "evidence": r.evidence,
                "context_tag": r.context_tag,
                "source_uri": r.source_uri,
            }
            for r in rules
        ],
        sort_keys=True,
    )
    digest = hashlib.sha256(payload.encode()).hexdigest()
    RuleVersion.objects.create(version=version, sha256=digest, steward=steward)


@shared_task
def nightly_self_audit():
    """Sanity sweep: any active rule without a citation or version is flagged."""
    orphans = InteractionRule.objects.filter(active=True).filter(
        source_uri=""
    ) | InteractionRule.objects.filter(active=True, rule_version__isnull=True)
    return [f"{r.pk}:{r.herb_a}" for r in orphans[:50]]
