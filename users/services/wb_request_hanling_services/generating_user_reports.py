import logging
import uuid
from django.db import transaction
from users.models import SaleObject, SaleReport

django_logger = logging.getLogger('django_logger')


def create_report_object(current_user, api_key, sale, unique_week_uuid):
    return SaleReport(
        api_key=api_key,
        owner=current_user,
        realizationreport_id=sale.realizationreport_id,
        unique_week_uuid=unique_week_uuid,
        year=sale.year,
        week_num=sale.week_num,
        month_num=sale.month_num,
        create_dt=sale.create_dt,
        date_from=sale.date_from,
        date_to=sale.date_to
    )


def generate_reports(current_user, api_key):
    """
    The function creates new user reports,
    assigns them unique identifiers of the week UUID4 and checks for reports duplicates for current user
    :param current_user:
    :param api_key: current WBApiKey of request user
    :return: returns None if success or transaction rollback if there are any errors
    """
    sale_objects = SaleObject.objects.filter(
        owner=current_user,
        api_key=api_key
    ).distinct('realizationreport_id').order_by('realizationreport_id')

    report_objects: list = []

    unique_weeks_uuid: dict = {}

    for sale in sale_objects:
        if SaleReport.objects.filter(api_key__is_current=True,
                                     api_key__user=current_user,
                                     realizationreport_id=sale.realizationreport_id).exists():
            continue

        if unique_weeks_uuid.get(sale.week_num, None):
            report_objects.append(create_report_object(current_user, api_key, sale, unique_weeks_uuid.get(sale.week_num)))
        else:
            new_uuid = uuid.uuid4()
            unique_weeks_uuid[sale.week_num] = new_uuid
            report_objects.append(create_report_object(current_user, api_key, sale, new_uuid))

    try:
        SaleReport.objects.bulk_create(report_objects)
    except Exception as err:
        django_logger.critical(
            f'Failed to create SaleReport objects for a user - {current_user.email}',
            exc_info=err
        )
        transaction.rollback()
