from typing import List

from users.models import UnloadedReports
from users.services.decrypt_api_key_service import get_decrypted_key
from users.services.wb_request_handling_services.generating_objects_services import get_unloaded_report_object
from users.services.wb_request_handling_services.generating_unique_respose_data_services import \
    get_sorted_unique_report_ids


import pandas as pd
import requests


def create_unloaded_report_objects(current_api_key, realizationreport_ids):

    UnloadedReports.objects.bulk_create(
        [get_unloaded_report_object(current_api_key, report_id) for report_id in realizationreport_ids]
    )


def send_request_for_sales(date_from: str, date_to: str, current_api_key) -> dict:
    """
    The function is responsible for sending a request to Wildberries
    :param date_from: Date in RFC3339 format. The date from which we load sales
    :param date_to: Date in RFC3339 format. The date on which we load sales
    :param current_api_key: Api user key to add it to query params in a query
    :return: Returns a dictionary including the status of the Wildberries request and a list of received objects.
    """

    headers = {
        'Authorization': get_decrypted_key(current_api_key.api_key)
    }

    query = {
        "dateFrom": date_from,
        "dateTo": date_to,
    }

    response = requests.get(
        'https://statistics-api.wildberries.ru/api/v1/supplier/reportDetailByPeriod',
        headers=headers,
        params=query
    )

    if response.status_code == 401:
        return {
            'status': False,
            'message': 'Wildberries не может распознать текущий API ключ. '
                       'Пожалуйста, введите ключ статистики.'
        }
    elif response.status_code != 200:
        return {
            'status': False,
            'message': 'Ошибка при попытке получения данных от Wildberries. Пожалуйста, попробуйте позже.'
        }

    data = response.json()

    if not data:
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }

    return {
        'status': True,
        'data': data
    }


def get_filtered_wildberries_response(current_api_key, response: pd.DataFrame) -> pd.DataFrame:
    """
    Since the Wildberries API can't return more than 100,000 objects, you need to filter
    and delete the last and related reports.
    The function that generates the unloaded reports is also called
    :param current_api_key:
    :param response: Pandas DataFrame
    :return: filtered Pandas DataFrame
    """

    unique_report_ids = get_sorted_unique_report_ids(response)

    for_delete_report_ids: List[int] = [unique_report_ids[-1], unique_report_ids[-1] - 1, unique_report_ids[-1] - 2]
    for_unload_report_ids = [report_id for report_id in for_delete_report_ids if report_id in unique_report_ids]
    create_unloaded_report_objects(current_api_key, for_unload_report_ids)

    response = response.query('realizationreport_id not in @for_delete_report_ids')

    return response


def get_wildberries_response(current_api_key, date_from: str, date_to: str) -> pd.DataFrame or dict:
    """
    The function forms a Pandas DataFrame from the response, which is the result of the wildberries response
    if the request to the WildBerries API was successful, otherwise it returns the status and message back to the client.

    It also checks the condition that the length of the list received from Wildberries is less than 100 thousand.
    If it is, then the Pandas DataFrame is returned.
    If the objects are 100 thousand, the DataFrame is filtered before returning the response.
    :param current_api_key: Api user key to add it to query params in a query
    :param date_from: Date in RFC3339 format. The date from which we load sales
    :param date_to: Date in RFC3339 format. The date on which we load sales
    :return: Pandas DataFrame or status and message if there was wrong response in dict
    """
    response = send_request_for_sales(date_from, date_to, current_api_key)

    if not response.get('status'):
        return response

    response_dataframe = pd.DataFrame(response['data'])

    if len(response['data']) < 100000:
        return response_dataframe

    filtered_response = get_filtered_wildberries_response(current_api_key, response_dataframe)

    return filtered_response
