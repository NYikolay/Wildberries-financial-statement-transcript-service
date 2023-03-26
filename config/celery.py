import os

from celery import Celery
from celery.schedules import crontab

import environ

env = environ.Env()
environ.Env.read_env()


os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env("SETTINGS_TYPE")}')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.timezone = 'Europe/Moscow'
