import logging
from datetime import date, datetime
import pytz
import requests

from django.core.mail import EmailMessage

from celery import shared_task, Task

from config.settings.base import EMAIL_HOST_USER, SSE_NOTIFICATION_SECRET, DJANGO_DOCKER_HOST

from users.models import WBApiKey, User
from users.services.generate_last_report_date_service import get_last_report_date
from users.services.wb_request_handling_services.execute_request_data_handling import \
    execute_wildberries_request_data_handling

celery_logger = logging.getLogger('celery_logger')


@shared_task()
def send_email_verification(mail_message, to_email, mail_subject):

    to_email = to_email
    try:
        email = EmailMessage(
            mail_subject, mail_message, to=[to_email], from_email=EMAIL_HOST_USER
        )
        email.send()
    except Exception as err:
        celery_logger.critical('Background sending of messages to email does not work', exc_info=err)


@shared_task(bind=True)
def execute_wildberries_reports_loading(self, current_key_id, current_user_id):
    current_api_key = WBApiKey.objects.get(id=current_key_id)
    current_user = User.objects.get(id=current_user_id)

    today_date = date.today()
    last_report_date = get_last_report_date(current_api_key)

    current_api_key.is_active_import = True
    current_api_key.save()

    try:
        report_status = execute_wildberries_request_data_handling(
            current_user,
            last_report_date,
            today_date,
            current_api_key
        )
    except Exception as err:
        celery_logger.critical(
            f'Failed to load reports for a user {current_user.email}',
            exc_info=err
        )
        current_api_key.is_active_import = False
        current_api_key.save()

        requests.post(
            f'{DJANGO_DOCKER_HOST}/events/notify/user/',
            data={
                "secret": SSE_NOTIFICATION_SECRET,
                "user_id": current_user.id,
                "status": "error",
                "message": 'Ошибка формирования отчёта. Пожалуйста, обратитесь в службу поддержки'
            }
        )

        return

    if report_status.get('status') is True:
        current_api_key.is_wb_data_loaded = True
        current_api_key.is_active_import = False
        current_api_key.last_reports_update = datetime.now().replace(tzinfo=pytz.timezone('Europe/Moscow'))
        current_api_key.save()

        requests.post(
            f'{DJANGO_DOCKER_HOST}/events/notify/user/',
            data={
                "secret": SSE_NOTIFICATION_SECRET,
                "user_id": current_user.id,
                "status": "success",
                "message": 'Данные успешно загружены'
            }
        )

        return

    current_api_key.is_active_import = False
    current_api_key.save()

    requests.post(
        f'{DJANGO_DOCKER_HOST}/events/notify/user/',
        data={
            "secret": SSE_NOTIFICATION_SECRET,
            "user_id": current_user.id,
            "status": "error",
            "message": f"{report_status.get('message')}"
        }
    )

    return



