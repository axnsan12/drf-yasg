import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True

SWAGGER_SETTINGS.update(
    {
        "VALIDATOR_URL": "http://localhost:8189",
    }
)

DATABASES = {
    "default": dj_database_url.parse(
        "sqlite:///" + os.path.join(BASE_DIR, "db.sqlite3")
    )
}
