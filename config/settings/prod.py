from config.settings.base import *


DEBUG = False

ALLOWED_HOSTS = [
    'app.commery.ru',
    '62.217.182.252',
    'web'
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
