import os

from .base import *  # noqa: F403

DEBUG = False

HOST_DOMAIN = os.environ.get("DJANGO_HOST_DOMAIN")
ALLOWED_HOSTS = [HOST_DOMAIN] if HOST_DOMAIN else []

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

HOST_URL = os.environ.get("DJANGO_HOST_URL")
CSRF_TRUSTED_ORIGINS = [HOST_URL] if HOST_URL else []

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

SILENCED_SYSTEM_CHECKS = [
    "security.W004",
    "security.W008",
]

MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

SWAGGER_SETTINGS.update(
    {
        "DEFAULT_API_URL": HOST_URL,
    }
)
