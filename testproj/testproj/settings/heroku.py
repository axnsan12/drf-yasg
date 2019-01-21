import dj_database_url

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS.append('.herokuapp.com')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
assert SECRET_KEY, 'DJANGO_SECRET_KEY environment variable must be set'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Database
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

SILENCED_SYSTEM_CHECKS = [
    'security.W004',  # SECURE_HSTS_SECONDS
    'security.W008',  # SECURE_SSL_REDIRECT
]
