from config.settings.base import *


DEBUG = False

ALLOWED_HOSTS = [
    'app.commery.ru',
    '62.217.182.252',
    'web',
    'webasgi',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
