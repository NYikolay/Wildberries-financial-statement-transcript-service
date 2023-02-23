from config.settings.base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

CSRF_TRUSTED_ORIGINS = []

INTERNAL_IPS = ['127.0.0.1', '0.0.0.0']

INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
