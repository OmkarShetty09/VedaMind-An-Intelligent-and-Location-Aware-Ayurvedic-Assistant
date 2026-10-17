from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bootstrap a superuser from the DEMO_EMAIL / DEMO_PASSWORD settings (.env)."

    def handle(self, *args, **options):
        User = get_user_model()
        email, password = settings.ADMIN_EMAIL.strip().lower(), settings.ADMIN_PASSWORD
        if not email or not password:
            self.stdout.write("DEMO_EMAIL / DEMO_PASSWORD not set in .env; no superuser created.")
            return
        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write("Superuser already exists.")
            return
        User.objects.create_superuser(email=email, name="Admin", password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser {email}"))
