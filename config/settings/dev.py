from config.settings.base import *
import socket

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '2be1-80-249-93-127.eu.ngrok.io']

CSRF_TRUSTED_ORIGINS = ['https://2be1-80-249-93-127.eu.ngrok.io']

INTERNAL_IPS = ['127.0.0.1', '2be1-80-249-93-127.eu.ngrok.io']

INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']

# tricks to have debug toolbar when developing with docker
ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + '1']
