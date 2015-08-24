"""
Django settings for SmoWeb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket
from pymongo import MongoClient

DEVELOPMENT_ENV = True
hostname = socket.gethostname()
#print 'Hostname: {0}'.format(hostname)
if (hostname.startswith('SmoWeb')):
	DEVELOPMENT_ENV = False

if (DEVELOPMENT_ENV):
	print("Development SetUp")
else:
	print("Production SetUp")
	
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret-key'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = DEVELOPMENT_ENV

TEMPLATE_DEBUG = False #DEVELOPMENT_ENV

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
		}
	},
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/srv/SmoWeb/Log/debug.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

if (DEVELOPMENT_ENV):
	ALLOWED_HOSTS = []
else:
	ALLOWED_HOSTS = ['.sysmoltd.com']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap_toolkit',
    'django_jinja',
    'SmoWebBase',
    'ThermoFluids',
    'BioReactors'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'SmoWeb.urls'

WSGI_APPLICATION = 'SmoWeb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

if (DEVELOPMENT_ENV):
	STATICFILES_DIRS = (
		('doc', os.path.join(BASE_DIR, "doc", "public", "build")),
	)
	STATIC_URL = '/static/'
else:
	STATIC_URL = '/static/'
STATIC_ROOT = '/srv/SmoWeb/Static/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

MEDIA_URL = '/media/'

if (DEVELOPMENT_ENV):
	MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
	MEDIA_ROOT = '/srv/SmoWeb/Media'

HDF_FOLDER = os.path.join(MEDIA_ROOT, "DataManagement","hdf")

# Celery task queue settings
# message_broker --> rabbitmq = amqp
BROKER_URL = 'amqp://guest@127.0.0.1:5672/'
CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
	"host": "127.0.0.1",
	"port": 27017,
	"database": "jobs",
	"taskmeta_collection": "stock_taskmeta_collection",
	"user": "dbUser",
	"password": "dbPassword",
	"ssl": True,
}

db = MongoClient('mongodb://dbUser:dbPassword@localhost:27017/SmoWeb', ssl = True)

TEMPLATE_LOADERS = (
    'django_jinja.loaders.FileSystemLoader',
    'django_jinja.loaders.AppLoader',
)

#DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.jinja'

import smo
JINJA_TEMPLATE_IMPORTS = {
	'smo': smo, 
	'isinstance': isinstance, 
	'issubclass': issubclass,
	'hasattr': hasattr
}