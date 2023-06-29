import os
import environ

from pathlib import Path

from config.json_logging_formatters import CustomJsonFormatter

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")
SECRET_CODE = env("SECRET_CODE")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'reports',
    'payments',
    'support',
    'django_otp',
    'django_celery_beat',
    'django_otp.plugins.otp_totp',
    'django_prometheus',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware'
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.user_additional_data_context.current_user_api_key',
                'users.context_processors.user_additional_data_context.user_last_report_date',
                'users.context_processors.user_additional_data_context.user_product_article',
                'users.context_processors.user_additional_data_context.general_report_message'
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT")
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'users.password_validators.LengthValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CELERY SETTINGS
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# CACHES
CACHES = {
    'default': {
        'BACKEND': env("CACHE_BACKAND"),
        'LOCATION': env("CACHE_LOCATION"),
    }
}

# REDIS SETTINGS
REDIS_HOST = env("REDIS_HOST")
REDIS_PORT = env("REDIS_PORT")

# REPORTS BOT SETTINGS
BOT_TOKEN = env("BOT_TOKEN")

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

# ROBOKASSA SETTINGS
ROBOKASSA_MERCHANT_LOGIN = env("MERCHANT_LOGIN")
ROBOKASSA_PASSWORD1 = env("ROBOKASSA_PASSWORD1")
ROBOKASSA_PASSWORD2 = env("ROBOKASSA_PASSWORD2")
IS_TEST_MODE = env("IS_TEST_MODE").lower() in ('true', '1', 't')
ROBOKASSA_TARGET_URL = 'https://auth.robokassa.ru/Merchant/Index/'
ROBOKASSA_TARGET_JSON_URL = 'https://auth.robokassa.ru/Merchant/Indexjson.aspx?'
ROBOKASSA_CULTURE = env("ROBOKASSA_CULTURE")


# DJANGO PROMETHEUS
PROMETHEUS_EXPORT_MIGRATIONS = False

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '{asctime} - {levelname} - {module} - {filename} - {message}',
            'style': '{',
        },
        'json_formatter': {
            '()': CustomJsonFormatter,
            'format': '%(asctime)s|%(levelname)s|%(pathname)s|%(funcName)s|%(lineno)d|[msg:%(message)s]|%(exc_info)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'django_logs_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'json_formatter',
            'filename': '/commery_project/logs/django_logs.json'
        },
        'celery_logs_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'json_formatter',
            'filename': '/commery_project/logs/celery_logs.json'
        }
    },
    'loggers': {
        'django_logger': {
            'level': env('LOGGER_LVL'),
            'handlers': ['console', 'django_logs_handler'],
            'propagate': False
        },
        'celery_logger': {
            'level': env('LOGGER_LVL'),
            'handlers': ['console', 'celery_logs_handler'],
            'propagate': False
        }
    },
}

