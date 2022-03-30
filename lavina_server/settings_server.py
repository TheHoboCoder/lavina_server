import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["172.21.210.1"]

CSRF_TRUSTED_ORIGINS = ['https://projects.masu.edu.ru','https://172.21.210.1']

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lavina_db',
        'USER' : 'lavina_user',
        'PASSWORD' : '1qw#109_&Hl=',
        'HOST' : '127.0.0.1',
        'PORT' : '5432',
    }
}
