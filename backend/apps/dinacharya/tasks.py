from celery import shared_task

from .models import DinacharyaRecommendation


@shared_task
def refresh_routines_for_users():
    """Regenerate today's routine for users with an existing one (season drift)."""
    from datetime import date

    from apps.users.models import User

    from .engine import build_routine, persist_routine

    day = date.today()
    user_ids = DinacharyaRecommendation.objects.filter(date=day).values_list("user_id", flat=True)
    done = 0
    for user in User.objects.filter(id__in=user_ids).iterator():
        try:
            persist_routine(user, build_routine(user))
            done += 1
        except Exception:
            continue
    return {"refreshed": done}
