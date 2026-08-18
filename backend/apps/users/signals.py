from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User


@receiver(post_save, sender=User)
def ensure_dosha_profile(sender, instance, created, **kwargs):
    """A user always has a dosha profile row (even if unscored)."""
    if created:
        from apps.dosha_profiles.models import DoshaProfile

        DoshaProfile.objects.get_or_create(user=instance)
