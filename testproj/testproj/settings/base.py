import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.urls import reverse_lazy

from testproj.util import static_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'test.local',
]
CORS_ORIGIN_ALLOW_ALL = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'oauth2_provider',
    'corsheaders',

    'drf_yasg',
    'snippets',
    'users',
    'articles',
    'todo',
    'people'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'drf_yasg.middleware.SwaggerExceptionMiddleware',
]

ROOT_URLCONF = 'testproj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'testproj', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'testproj.wsgi.application'

LOGIN_URL = reverse_lazy('admin:login')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

OAUTH2_CLIENT_ID = '12ee6bgxtpSEgP8TioWcHSXOiDBOUrVav4mRbVEs'
OAUTH2_CLIENT_SECRET = '5FvYALo7W4uNnWE2ySw7Yzpkxh9PSf5GuY37RvOys00ydEyph64dbl1ECOKI9ceQ' \
                       'AKoz0JpiVQtq0DUnsxNhU3ubrJgZ9YbtiXymbLGJq8L7n4fiER7gXbXaNSbze3BN'
OAUTH2_APP_NAME = 'drf-yasg OAuth2 provider'

OAUTH2_REDIRECT_URL = static_lazy('drf-yasg/swagger-ui-dist/oauth2-redirect.html')
OAUTH2_AUTHORIZE_URL = reverse_lazy('oauth2_provider:authorize')
OAUTH2_TOKEN_URL = reverse_lazy('oauth2_provider:token')

# drf-yasg
SWAGGER_SETTINGS = {
    'LOGIN_URL': reverse_lazy('admin:login'),
    'LOGOUT_URL': '/admin/logout',
    'PERSIST_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,

    'DEFAULT_INFO': 'testproj.urls.swagger_info',

    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'in': 'header',
            'name': 'Authorization',
            'type': 'apiKey',
        },
        'OAuth2 password': {
            'flow': 'password',
            'scopes': {
                'read': 'Read everything.',
                'write': 'Write everything,',
            },
            'tokenUrl': OAUTH2_TOKEN_URL,
            'type': 'oauth2',
        },
        'Query': {
            'in': 'query',
            'name': 'auth',
            'type': 'apiKey',
        },
    },
    'OAUTH2_REDIRECT_URL': OAUTH2_REDIRECT_URL,
    'OAUTH2_CONFIG': {
        'clientId': OAUTH2_CLIENT_ID,
        'clientSecret': OAUTH2_CLIENT_SECRET,
        'appName': OAUTH2_APP_NAME,
    },
    "DEFAULT_PAGINATOR_INSPECTORS": [
        'testproj.inspectors.UnknownPaginatorInspector',
        'drf_yasg.inspectors.DjangoRestResponsePagination',
        'drf_yasg.inspectors.DrfAPICompatInspector',
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ]
}

REDOC_SETTINGS = {
    'SPEC_URL': ('schema-json', {'format': '.json'}),
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'testproj', 'static'),
]

# Testing
TEST_RUNNER = 'testproj.runner.PytestTestRunner'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'pipe_separated': {
            'format': '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        }
    },
    'handlers': {
        'console_log': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'pipe_separated',
        },
    },
    'loggers': {
        'drf_yasg': {
            'handlers': ['console_log'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'swagger_spec_validator': {
            'handlers': ['console_log'],
            'level': 'INFO',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console_log'],
        'level': 'INFO',
    }
}
