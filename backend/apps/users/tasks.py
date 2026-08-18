from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import User


@shared_task
def send_consent_confirmation_email(user_id):
    """Placeholder: notify user their consent + data usage was recorded."""
    user = User.objects.filter(id=user_id).first()
    if user:
        return f"consent recorded for {user.email}"
    return "user not found"


@shared_task
def deactivate_inactive_users(days=365):
    cutoff = timezone.now() - timedelta(days=days)
    return User.objects.filter(last_login__isnull=True, date_joined__lt=cutoff).update(is_active=False)
