import os

import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_placeholder.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Default superuser credentials
SUPERUSER_USERNAME = "admin"
SUPERUSER_EMAIL = "admin@example.com"
SUPERUSER_PASSWORD = "admin123"


def create_superuser():
    if not User.objects.filter(username=SUPERUSER_USERNAME).exists():
        User.objects.create_superuser(
            username=SUPERUSER_USERNAME,
            email=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD,
        )
        print(f"Superuser '{SUPERUSER_USERNAME}' created successfully!")
    else:
        print(f"Superuser '{SUPERUSER_USERNAME}' already exists.")


if __name__ == "__main__":
    create_superuser()
