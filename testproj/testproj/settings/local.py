from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True

SWAGGER_SETTINGS.update(
    {
        "VALIDATOR_URL": "http://localhost:8189",
    }
)
