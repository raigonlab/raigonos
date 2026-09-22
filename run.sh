#!/bin/bash
# Convenience script: activate venv and start the local dev server.
cd "$(dirname "$0")"
source venv/bin/activate
python manage.py runserver
