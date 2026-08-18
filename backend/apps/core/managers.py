from django.db.models import Manager, QuerySet


class ActiveQuerySet(QuerySet):
    def active(self):
        return self.filter(active=True)

    def by_user(self, user):
        return self.filter(user=user)


class ActiveManager(Manager):
    def get_queryset(self):
        return ActiveQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()
