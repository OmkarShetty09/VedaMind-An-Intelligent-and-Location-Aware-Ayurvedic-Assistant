import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Sequence(lambda n: f"user{n}@vedamind.local")
    name = factory.Faker("name")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "password123!")


class WithConsentMixin:
    """Set consent flags so guardrail-protected views are reachable in tests."""

    @factory.post_generation
    def consent(self, create, extracted, **kwargs):
        if create:
            self.consent_accepted = True
            self.save(update_fields=["consent_accepted"])
