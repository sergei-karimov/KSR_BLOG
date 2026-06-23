from .base import *

DEBUG = True

INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.postgres']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
