from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from .models import GuardrailDecision


@shared_task
def daily_digest():
    """Summarize yesterday's guardrail decisions for the clinician steward."""
    from django.db.models import Count

    since = timezone.now() - timezone.timedelta(days=1)
    counts = dict(
        GuardrailDecision.objects.filter(created_at__gte=since)
        .values_list("decision")
        .annotate(count=Count("id"))
    )
    try:
        send_mail(
            subject="VedaMind guardrail digest",
            message=f"Decisions in last 24h: {counts}",
            from_email=None,
            recipient_list=["steward@vedamind.app"],
            fail_silently=True,
        )
    except Exception:
        pass
    return counts
