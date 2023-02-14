import logging
from datetime import datetime

from django.core.mail import EmailMessage
from django.db import transaction
from django.core.cache import cache


from celery import shared_task

from config.settings.base import EMAIL_HOST_USER
from users.models import ClientUniqueProduct, User, WBApiKey
from users.services.generate_unique_articles_obj import handle_unique_articles
from users.services.generating_user_products_data import get_article_additional_data

celery_logger = logging.getLogger('celery_logger')


@shared_task()
def send_email_verification(mail_message, to_email, mail_subject):

    to_email = to_email

    email = EmailMessage(
        mail_subject, mail_message, to=[to_email], from_email=EMAIL_HOST_USER
    )
    email.send()

