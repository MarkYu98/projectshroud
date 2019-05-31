"""
Django settings for projectshroud project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from os import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vwkud5fp9h+y$mpg()^8ws()9e+p#1ad+4dfs#@tr62$icn#42'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    'backend.apps.BackendConfig',
    'algoliasearch_django',
    'huey.contrib.djhuey',
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

ROOT_URLCONF = 'projectshroud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['frontend/dist'],
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

FILES_DIR = os.path.join(BASE_DIR, "files")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/dist/static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

WSGI_APPLICATION = 'projectshroud.wsgi.application'

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

AUTH_USER_MODEL = 'backend.UserProfile'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if environ.get('DJANGO_DB') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
            'NAME': 'shrouddb',
    	    'USER': environ.get('MYSQL_USER'),                # 数据库用户名
            'PASSWORD': environ.get('MYSQL_PSW'),             # 密码
            'HOST': 'localhost',    # 主机
            'PORT': '3306',         # 数据库使用的端口
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # Not work properly
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# Django-allauth registration
SITE_ID = 1

ACCOUNT_ADAPTER = 'backend.adapters.AccountAdapter'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'None'
ACCOUNT_AUTHENTICATION_METHOD = 'mobile'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'mobile'
ACCOUNT_USERNAME_REQUIRED = True

# Algolia search
ALGOLIA = {
    'APPLICATION_ID': 'WN4Q0PFNA4',
    'API_KEY': 'ea0e9f826c9dc709941f8260e7ca30fd'
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.testshroud.top'
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_HOST_USER = 'noreply@testshroud.top'
EMAIL_HOST_PASSWORD = '5LingFournoreply'
DEFAULT_FROM_EMAIL = 'noreply <%s>' % EMAIL_HOST_USER

SITE_OFFICIAL_NAME = 'TESTSHROUD'
if environ.get('DJANGO_DB') == 'mysql':
    SITE_HOST_NAME = '47.94.219.224:8000'
else:
    SITE_HOST_NAME = 'localhost:8000'
SITE_DOMAIN_NAME = 'testshroud.top'

USER_ACTIVATE_URL = '/send/activation/'

# Cache
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#         # 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

from huey import SqliteHuey

# HUEY = SqliteHuey('scheduled_job', filename='huey.sqlite3')

HUEY = {
    'huey_class': 'huey.SqliteHuey',
    'name': 'scheduled_job',
    'filename': 'huey.sqlite3',
    'immediate': False
    # 'utc': False
}
