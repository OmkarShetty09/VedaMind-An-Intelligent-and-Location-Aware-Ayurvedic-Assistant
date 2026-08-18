from celery import shared_task

from .models import Conversation


@shared_task
def purge_deleted(days=30):
    from django.utils import timezone

    cutoff = timezone.now() - timezone.timedelta(days=days)
    return Conversation.objects.filter(deleted_at__lt=cutoff).delete()[0]
