from django.conf import settings
from rest_framework.settings import APISettings

SWAGGER_DEFAULTS = {
    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'LOGIN_URL': getattr(settings, 'LOGIN_URL', None),
    'LOGOUT_URL': getattr(settings, 'LOGOUT_URL', None),
    'VALIDATOR_URL': '',

    'OPERATIONS_SORTER': None,
    'TAGS_SORTER': None,
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': False,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'model',
    'DEFAULT_MODEL_DEPTH': 2,
}

REDOC_DEFAULTS = {
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': False,
}

IMPORT_STRINGS = []

#:
swagger_settings = APISettings(
    user_settings=getattr(settings, 'SWAGGER_SETTINGS', {}),
    defaults=SWAGGER_DEFAULTS,
    import_strings=IMPORT_STRINGS,
)

#:
redoc_settings = APISettings(
    user_settings=getattr(settings, 'REDOC_SETTINGS', {}),
    defaults=REDOC_DEFAULTS,
    import_strings=IMPORT_STRINGS,
)
