import logging
from typing import List

import pandas as pd
from django.db import transaction

from users.models import IncorrectReport
from users.services.wb_request_handling_services.generating_objects_services import get_incorrect_report_object

django_logger = logging.getLogger('django_logger')


def create_incorrect_reports(current_user, current_api_key, incorrect_reports: pd.DataFrame) -> None:
    """
    The function is designed to create IncorrectReport model objects in the database.

    First of all it checks if the Pandas DataFrame is empty, if it is, it means that user has no incorrect reports
    and therefore we can delete all IncorrectReport objects created earlier in the IncorrectReport database.
    Why do we do this?
    Because if we have found the incorrect reports during the previous loading from the Wildberries API
    all the subsequent loading we do from the date of the earliest incorrect report and consequently we can safely
    remove all the incorrect IncorrectReport objects, if during the current loading all the reports are correct.

    If incorrect reports were detected during data processing, we retrieve the
    IncorrectReport objects from the database in order to avoid duplicates

    In the try except block we iterate over the DataFrame passed in the Pandas parameters and
    call the get_incorrect_report_object function, which forms an instance of the IncorrectReport class.
    Then using bulk_create we send a request to the database to create objects

    :param current_user: User object, authorized user
    :param current_api_key: WBApiKey object, active api key
    :param incorrect_reports: Pandas DataFrame with incorrect report data
    :return: None
    """

    if incorrect_reports.empty:
        IncorrectReport.objects.filter(owner=current_user, api_key=current_api_key).delete()
        return None

    generated_incorrect_reports: List[int] = IncorrectReport.objects.filter(
        owner=current_user,
        api_key=current_api_key
    ).values_list('realizationreport_id', flat=True)

    try:
        reports_to_create: list = [get_incorrect_report_object(current_user, row, current_api_key)
                                   for row in incorrect_reports.itertuples()
                                   if row.realizationreport_id not in generated_incorrect_reports]

        IncorrectReport.objects.bulk_create(reports_to_create)
    except Exception as err:
        django_logger.error(
            f'Error during the loading of a broken report from a user - {current_user.email}',
            exc_info=err
        )
        transaction.rollback()
