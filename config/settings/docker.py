"""
Django settings for tucat project.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import environ

# OK Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path('tucat')

env = environ.Env(DEBUG=(bool, False),)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# OK SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = '4d!2@*cmd5)xz$s#jt9xt8dcox2om!78a^=+wy!dyyf)9b!lkj'
SECRET_KEY = env('SECRET_KEY')

# OK SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# TODO
ALLOWED_HOSTS = [
    'localhost',
    'dotucat.nowchess.org'
]

# OK APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',
)
THIRD_PARTY_APPS = (
    'crispy_forms',  # Form layouts
    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    'allauth.socialaccount.providers.twitter',
    'django_celery_beat',
    'django_celery_results',
    'admin_interface',
    'colorfield',
    # Admin after django-admin-interface
    'django.contrib.admin',
    #'private_storage',
)

# OK Apps specific for this project go here.
LOCAL_APPS = (
    'tucat.users',  # custom users app
    'tucat.core',
    'tucat.application',
)

# OK See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# OK
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# OK
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
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

# OK FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = [str(ROOT_DIR.path('config/fixtures'))]

# OK Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    },
}

MONGO_CLIENT = 'mongodb://%s:%s@mongodb:27017' % ( env('MONGO_INITDB_ROOT_USERNAME'), env('MONGO_INITDB_ROOT_PASSWORD'))



# OK AUTHENTICATION CONFIGURATION
# Required for Django-allauth http://django-allauth.readthedocs.io/en/latest/installation.html
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# OK Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'

# OK Redirects to the administration after successful login
LOGIN_REDIRECT_URL = '/admin'
LOGIN_URL = 'account_login'

# OK SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

# OK LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(module)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': env('LOGLEVEL'),
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': env('LOGLEVEL'),
            'class': 'logging.FileHandler',
            'filename': env('APPLOG') + '/logging.log',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'root': {
            'handlers': ['file', 'console'],
            'level': env('LOGLEVEL'),
        },
        'core': {
            'handlers': ['file', 'console'],
            'level': env('LOGLEVEL'),
        },
        'application': {
            'handlers': ['file', 'console'],
            'level': env('LOGLEVEL'),
        },
        'twitter_extraction': {
            'handlers': ['file', 'console'],
            'level': env('LOGLEVEL'),
        },
        'twitter_streaming': {
            'handlers': ['file','console'],
            'level': env('LOGLEVEL'),
        },
    }
}

# OK See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
# Required for Django-allauth http://django-allauth.readthedocs.io/en/latest/installation.html
SITE_ID = 1

# OK
WSGI_APPLICATION = 'config.wsgi.application'

# OK Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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


# OK Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Brussels'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# OK STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'staticfiles')

# OK https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# OK https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

# OK https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# OK MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))
#MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'media')

# OK https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# OK URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# OK Celery settings always start with CELERY_ even with the new settings
# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
# http://docs.celeryproject.org/en/latest/userguide/configuration.html

env('RABBITMQ_DEFAULT_USER')
#CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672/'
CELERY_BROKER_URL = 'amqp://%s:%s@rabbitmq:5672%s' % ( env('RABBITMQ_DEFAULT_USER'),
env('RABBITMQ_DEFAULT_PASS'), env('RABBITMQ_DEFAULT_VHOST') )
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_WORKER_CONCURRENCY=1
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
