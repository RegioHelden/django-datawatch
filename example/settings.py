import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&kxa67(_phgs@5&8=!x(ix(l%w1nmkh&n#1%^5pm&wm^ij)4(6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'django_celery_beat',
    'django_datawatch.apps.DjangoDatawatchConfig',
    'example.apps.ExampleConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'example.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'example.wsgi.application'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'example/locale'),
    os.path.join(BASE_DIR, 'django_datawatch/locale'),
)

# Database
if 'TOX_ENV_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     'postgres',
            'USER':     'postgres',
            'PASSWORD': 'postgres',
            'HOST':     'localhost',
            'PORT':     '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'app',
            'USER': 'app',
            'PASSWORD': 'app',
            'HOST': 'datawatch-db',
            'PORT': '5432',
        },
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)d %(funcName)s %(process)d '
                      '%(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

BROKER_URL = 'amqp://datawatch-rabbitmq'

LOGIN_URL = '/admin/'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

BOOTSTRAP5 = {'horizontal_label_class': 'col-md-2', 'horizontal_field_class': 'col-md-10', 'success_css_class': ''}

DJANGO_DATAWATCH_BACKEND = 'django_datawatch.backends.synchronous'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'