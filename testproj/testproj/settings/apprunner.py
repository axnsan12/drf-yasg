import dj_database_url
import os
import whitenoise

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS.append(".awsapprunner.com")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
assert SECRET_KEY, "DJANGO_SECRET_KEY environment variable must be set"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Database
DATABASES = {
    "default": dj_database_url.config(default="sqlite:///db.sqlite3", conn_max_age=600)
}

SILENCED_SYSTEM_CHECKS = [
    "security.W004",  # SECURE_HSTS_SECONDS
    "security.W008",  # SECURE_SSL_REDIRECT
]

MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
