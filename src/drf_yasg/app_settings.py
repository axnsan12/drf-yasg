from django.conf import settings
from rest_framework.settings import perform_import

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
    'DEFAULT_MODEL_DEPTH': 3,
}

REDOC_DEFAULTS = {
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': False,
}

IMPORT_STRINGS = []


class AppSettings(object):
    """
    Stolen from Django Rest Framework, removed caching for easier testing
    """

    def __init__(self, user_settings, defaults, import_strings=None):
        self._user_settings = user_settings
        self.defaults = defaults
        self.import_strings = import_strings or []

    @property
    def user_settings(self):
        return getattr(settings, self._user_settings, {})

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid setting: '%s'" % attr)  # pragma: no cover

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        return val


#:
swagger_settings = AppSettings(
    user_settings='SWAGGER_SETTINGS',
    defaults=SWAGGER_DEFAULTS,
    import_strings=IMPORT_STRINGS,
)

#:
redoc_settings = AppSettings(
    user_settings='REDOC_SETTINGS',
    defaults=REDOC_DEFAULTS,
    import_strings=IMPORT_STRINGS,
)
