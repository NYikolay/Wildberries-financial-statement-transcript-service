import logging
from typing import List

from django.db import transaction

from users.models import UnloadedReports, SaleReport, ClientUniqueProduct
from users.services.wb_request_hanling_services.generating_incorrect_reports_service import create_incorrect_reports

from users.services.wb_request_hanling_services.generating_products_objs_service import generate_user_products
from users.services.wb_request_hanling_services.generating_sale_objects_service import create_sale_objects
from users.services.wb_request_hanling_services.generating_unique_respose_data_services import \
    get_sorted_unique_report_ids, get_unique_nm_ids
from users.services.wb_request_hanling_services.generating_user_reports_service import generate_reports
from users.services.wb_request_hanling_services.handling_wildberries_request_services import get_wildberries_response
from users.services.wb_request_hanling_services.reports_validation_services import get_incorrect_reports

import pandas as pd

django_logger = logging.getLogger('django_logger')


def check_reports_privacy(current_user, unique_reports_ids: List[int]) -> bool:
    """
    The function sends a query to the database to check the existing SaleReport from the data downloaded
    from Wildberries, excluding the current user

    This is caused by the need to check that the user has not created a new account and is trying to download his key
    again, avoiding payment and using only the trial version of the service
    :param current_user: User object, authorized user
    :param unique_reports_ids: A list of unique realizationreport_ids from the data set provided by Wildberries
    :return: True or False
    """
    return SaleReport.objects.filter(realizationreport_id__in=unique_reports_ids).exclude(owner=current_user).exists()


def get_existing_products(unique_nm_ids: List[int]) -> dict:
    """
    The function sends a query to the database to retrieve all ClientUniqueProduct objects whose nm_id
    is contained in unique_nm_ids

    :param unique_nm_ids:  list of unique nm_ids from the data set provided by Wildberries
    :return: {int: ClientUniqueProduct(), int: ClientUniqueProduct(), ....}
    """
    return ClientUniqueProduct.objects.in_bulk(unique_nm_ids, field_name='nm_id')


def get_existing_reports_ids(current_user, current_api_key) -> List[int]:
    """
    The function sends a query to the database to get the list of all SaleReports of the current
    user by the active WBApiKey
    :param current_user: User object, authorized user
    :param current_api_key: WBApiKey object, active api key
    :return: List of realizationreport_ids
    """
    existing_reports_ids = SaleReport.objects.filter(
        owner=current_user,
        api_key=current_api_key
    ).values_list('realizationreport_id', flat=True)

    return existing_reports_ids


def delete_unloaded_reports(current_api_key, existing_reports_ids: List[int]):
    """
    The function sends a query to the database to delete all linked UnloadedReports
    of an authorized user by the active WBApiKey and filtering by the occurrence of the existing_reports_id in the passed existing_reports_ids
    :param current_api_key: WBApiKey object, active api key
    :param existing_reports_ids:
    :return: None
    """
    UnloadedReports.objects.filter(
        api_key=current_api_key,
        realizationreport_id__in=existing_reports_ids
    ).delete()


def execute_wildberries_request_data_handling(current_user, date_from: str, date_to, current_api_key):
    response: pd.DataFrame or dict = get_wildberries_response(current_api_key, date_from, date_to)

    if response.get('status') is False:
        return response

    unique_reports_ids: List[int] = get_sorted_unique_report_ids(response).tolist()
    unique_nm_ids: List[int] = get_unique_nm_ids(response).tolist()
    incorrect_reports: pd.DataFrame = get_incorrect_reports(response)

    if check_reports_privacy(current_user, unique_reports_ids):
        django_logger.info(
            f"Attempted piracy, user - {current_user.email} "
            f"tries to upload someone else's reports or another account's reports"
        )
        return {
            'status': False,
            'message': 'Отчёты принадлежат другому пользователю.'
        }

    try:
        generate_user_products(current_user, set(unique_nm_ids), current_api_key)
    except Exception as err:
        django_logger.critical(
            f'Failed to create product objects for a user - {current_user.email}',
            exc_info=err
        )
        return {
            'status': False,
            'message': 'Произошла ошибка во время загрузки отчёта. Пожалуйста, обратитесь в службу поддержки.'
        }

    existing_products: dict = get_existing_products(unique_nm_ids)
    existing_reports_ids: List[int] = get_existing_reports_ids(current_user, current_api_key)

    try:
        with transaction.atomic():

            create_incorrect_reports(current_user, current_api_key, incorrect_reports)

            sale_objects_creating_status = create_sale_objects(
                current_user,
                current_api_key,
                response,
                existing_reports_ids,
                incorrect_reports['realizationreport_id'].values.tolist(),
                existing_products
            )

            if not sale_objects_creating_status.get('status'):
                return sale_objects_creating_status

            generate_reports(current_user, current_api_key)

            delete_unloaded_reports(current_api_key, existing_reports_ids)

    except Exception as err:
        django_logger.critical(
            f'Failed to load reports into the database for a user {current_user.email}',
            exc_info=err
        )
        return {
            'status': False,
            'message': 'Произошла ошибка во время загрузки отчёта. Пожалуйста, обратитесь в службу поддержки.'
        }

    return {
        'status': True
    }
