from config.settings.base import *
import socket

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', ]

CSRF_TRUSTED_ORIGINS = []

INTERNAL_IPS = ['127.0.0.1']

# INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
# MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']
#
# ip = socket.gethostbyname(socket.gethostname())
# INTERNAL_IPS += [ip[:-1] + '1']
