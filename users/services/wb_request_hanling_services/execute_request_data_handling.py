import logging
from typing import List

from django.db import transaction
from users.models import SaleReport, UnloadedReports, ClientUniqueProduct
from users.services.wb_request_hanling_services.generating_sale_objects_service import create_sale_objects
from users.services.wb_request_hanling_services.generating_unique_articles_service import get_unique_articles
from users.services.wb_request_hanling_services.generating_unique_reports_service import get_unique_reports

from users.services.wb_request_hanling_services.generating_user_reports_service import generate_reports
from users.services.wb_request_hanling_services.generating_incorrect_reports_service import generate_incorrect_reports
from users.services.wb_request_hanling_services.generating_products_objs_service import generate_user_products
from users.services.wb_request_hanling_services.reports_validation_service import get_incorrect_reports_lst
from users.services.wb_request_hanling_services.wildberries_request_handling_service import \
    get_wildberries_response_data

django_logger = logging.getLogger('django_logger')


def execute_wildberries_request_data_handling(current_user, date_from: str, date_to, current_api_key) -> dict:
    """
    The main function of requesting data from Wildberries. Combines all services related to data uploading.
    Checks for piracy, generates a list of SaleObject models instances.
    :param current_user:
    :param date_from: date for sending a request to WIldberries in query params
    :param date_to: date for sending a request to WIldberries in query params
    :param current_api_key: WBApiKey object of the current user
    :return: Return the status of all functions that work with data from Wildberries in the view.
    """

    res_dict: dict = get_wildberries_response_data(date_from, date_to, current_api_key)
    if not res_dict.get('status'):
        return res_dict

    incorrect_reports: dict = get_incorrect_reports_lst(res_dict.get('data'))
    unique_articles: list = get_unique_articles(res_dict.get('data'))
    unique_reports_ids: set = get_unique_reports(res_dict.get('data'))

    if SaleReport.objects.filter(realizationreport_id__in=unique_reports_ids).exclude(owner=current_user).exists():
        django_logger.info(
            f"Attempted piracy, user - {current_user.email} "
            f"tries to upload someone else's reports or another account's reports"
        )
        return {
            'status': False,
            'message': 'Отчёты принадлежат другому пользователю.'
        }

    try:
        generate_user_products(current_user, unique_articles, current_api_key)
    except Exception as err:
        django_logger.critical(
            f'Failed to create product objects for a user - {current_user.email}',
            exc_info=err
        )
        return {
            'status': False,
            'message': 'Произошла ошибка во время загрузки отчёта. Пожалуйста, обратитесь в службу поддержки.'
        }

    current_product_objs = ClientUniqueProduct.objects.in_bulk(
        [article_data.get('nm_id') for article_data in unique_articles], field_name='nm_id')

    generated_reports_ids = SaleReport.objects.filter(
        owner=current_user,
        api_key=current_api_key
    ).values_list('realizationreport_id', flat=True)

    try:
        with transaction.atomic():

            generate_incorrect_reports(
                current_user,
                incorrect_reports.get('incorrect_reports_data_list'),
                current_api_key
            )

            sale_objects_creating_status = create_sale_objects(
                current_user,
                current_api_key,
                res_dict.get('data'),
                generated_reports_ids,
                incorrect_reports,
                current_product_objs
            )

            if not sale_objects_creating_status.get('status'):
                return sale_objects_creating_status

            generate_reports(current_user, current_api_key)

            UnloadedReports.objects.filter(
                api_key=current_api_key,
                realizationreport_id__in=generated_reports_ids
            ).delete()
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
