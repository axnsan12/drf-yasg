import dj_database_url

from .base import *

SWAGGER_SETTINGS.update({'VALIDATOR_URL': 'http://localhost:8189'})

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

db_path = os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': dj_database_url.parse('sqlite:///' + db_path)
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!z1yj(9uz)zk0gg@5--j)bc4h^i!8))r^dezco8glf190e0&#p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

