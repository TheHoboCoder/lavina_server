ALLOWED_HOSTS = []

CSRF_TRUSTED_ORIGINS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'lavina_db',
        'USER' : 'lavina_user',
        'PASSWORD' : '1qw#109_&Hl=',
        'HOST' : 'localhost',
        'PORT' : '5432',
    }
}
