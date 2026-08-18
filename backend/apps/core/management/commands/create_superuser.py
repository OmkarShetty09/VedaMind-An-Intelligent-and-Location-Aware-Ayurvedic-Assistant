import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bootstrap a superuser from DEMO_EMAIL/DEMO_PASSWORD env vars."

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.environ.get("DEMO_EMAIL", "admin@vedamind.local")
        password = os.environ.get("DEMO_PASSWORD", "change-me")
        if User.objects.filter(email=email).exists():
            self.stdout.write("Superuser already exists.")
            return
        User.objects.create_superuser(email=email, name="Admin", password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser {email}"))
