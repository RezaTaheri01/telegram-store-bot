#!/bin/bash

# echo "Creating virtual environment..."
# python3 -m venv .venv

# echo "Activating virtual environment..."
# # For Linux/macOS:
# source .venv/bin/activate
# # For Windows (Git Bash / WSL):
# # source .venv/Scripts/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r req.txt

echo "Applying migrations..."
python manage.py makemigrations users payment products
python manage.py migrate

echo "Creating superuser..."
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin12345678

python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()

username = "$DJANGO_SUPERUSER_USERNAME"
email = "$DJANGO_SUPERUSER_EMAIL"
password = "$DJANGO_SUPERUSER_PASSWORD"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created.")
else:
    print("Superuser already exists.")
END

echo "Setup complete!"
