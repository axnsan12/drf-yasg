import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = (
    os.environ["DJANGO_ALLOWED_HOSTS"].split(",")
    if "DJANGO_ALLOWED_HOSTS" in os.environ
    else []
)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = (
    os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"].split(",")
    if "DJANGO_CSRF_TRUSTED_ORIGINS" in os.environ
    else []
)

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DATABASES = {
    "default": dj_database_url.config(default="sqlite:///db.sqlite3", conn_max_age=600)
}

SILENCED_SYSTEM_CHECKS = [
    "security.W004",
    "security.W008",
]

MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
