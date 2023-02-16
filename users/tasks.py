import logging

from django.core.mail import EmailMessage

from celery import shared_task

from config.settings.base import EMAIL_HOST_USER

celery_logger = logging.getLogger('celery_logger')


@shared_task()
def send_email_verification(mail_message, to_email, mail_subject):

    to_email = to_email

    email = EmailMessage(
        mail_subject, mail_message, to=[to_email], from_email=EMAIL_HOST_USER
    )
    email.send()

