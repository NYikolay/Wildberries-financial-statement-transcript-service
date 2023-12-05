from config.settings.base import *

DEBUG = False

ALLOWED_HOSTS = [
    '45.146.165.193',
    'web',
    'webasgi',
    'test.commery.ru'
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
