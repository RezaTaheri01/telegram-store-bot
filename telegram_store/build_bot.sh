#!/bin/bash

# echo "Creating virtual environment..."
# python -m venv .venv

# echo "Activating virtual environment..."
# # # For Linux/macOS:
# source .venv/bin/activate
# # # For Windows (Git Bash / WSL):
# # source .venv/Scripts/activate

echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r req.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying migrations..."
python manage.py makemigrations users payment products
python manage.py migrate

echo "Setup complete!"
