import logging
import requests
from django.core.mail import EmailMessage

from celery import shared_task

from config.settings.base import EMAIL_HOST_USER, BOT_TOKEN

celery_logger = logging.getLogger('celery_logger')


@shared_task()
def send_user_report_to_chat(text: str):
    token = BOT_TOKEN
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    channel_ids = [662937421, 115566666]

    for channel_id in channel_ids:
        response = requests.post(url, data={
            "chat_id": channel_id,
            "text": text
        })
        if response.status_code != 200:
            celery_logger.error('Sending messages through the bot doesn"t work')
