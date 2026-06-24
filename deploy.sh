#!/bin/bash
set -e

echo "==> Pulling latest code"
git pull

echo "==> Installing dependencies"
pip install -r requirements.txt

echo "==> Running migrations"
python manage.py migrate --settings=myblog.settings.production

echo "==> Syncing posts"
python manage.py sync_posts --settings=myblog.settings.production

echo "==> Collecting static files"
python manage.py collectstatic --noinput --settings=myblog.settings.production

echo "==> Notifying subscribers"
python manage.py notify_subscribers --settings=myblog.settings.production

echo "==> Reloading Gunicorn"
pkill -HUP gunicorn || true

echo "==> Done"
