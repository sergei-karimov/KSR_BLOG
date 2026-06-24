#!/bin/bash
set -e

VENV_DIR="$(dirname "$0")/venv"
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
fi

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
if pgrep -x gunicorn > /dev/null; then
    pkill -HUP gunicorn
    echo "Gunicorn reloaded."
else
    echo "WARNING: Gunicorn is not running. Start it manually." >&2
    exit 1
fi

echo "==> Done"
