import os

import dj_database_url

from .base import *  # noqa: F403

SWAGGER_SETTINGS.update({"VALIDATOR_URL": "http://localhost:8189"})

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

db_path = os.path.join(BASE_DIR, "db.sqlite3")
DATABASES = {"default": dj_database_url.parse("sqlite:///" + db_path)}

# Quick-start development settings - unsuitable for production

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
