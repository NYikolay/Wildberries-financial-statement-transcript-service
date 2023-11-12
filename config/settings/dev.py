from config.settings.base import *
import socket

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "web", "bd04-31-24-90-80.ngrok-free.app"]

CSRF_TRUSTED_ORIGINS = ['https://bd04-31-24-90-80.ngrok-free.app']

INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']

ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + '1']
