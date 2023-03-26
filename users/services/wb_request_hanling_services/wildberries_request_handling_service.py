import datetime
from typing import List

from users.models import UnloadedReports
from users.services.decrypt_api_key_service import get_decrypted_key
import requests

from users.services.wb_request_hanling_services.generating_unique_reports_service import get_unique_reports


def handle_unload_report_obj(current_api_key, report_id: int):
    return UnloadedReports(
        api_key=current_api_key,
        realizationreport_id=report_id
    )


def send_request_for_sales(date_from: str, date_to: str, current_api_key) -> dict:
    """
    The function is responsible for sending a request to Wildberries
    :param date_from: date_from: date for sending a request to WIldberries in query params
    :param date_to: date_from: date for sending a request to WIldberries in query params
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
    data = response.json()

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

    if not data:
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }

    return {
        'status': True,
        'data': data
    }


def get_wb_request_response(wildberries_response, current_api_key) -> dict:
    """
    The function processes and returns a request to Wildberries.
    For lists that are longer than 100.000 objects the logic of deleting last reports is used,
    otherwise the list goes further into processing.
    This is caused by the fact that Wildberries can't give more than 100.000 sales
    and it's necessary to load them in parts.
    :param wildberries_response:
    :param current_api_key: Api user key to add it to query params in a query
    :return: Returns a dictionary including the status of the Wildberries request and a list of received objects.
    """

    handled_response_data: dict = {
        'status': True,
        'data': []
    }

    unique_report_ids: List[int] = list(get_unique_reports(wildberries_response.get('data')))
    unique_report_ids.sort()
    for_delete_report_ids: List[int] = [unique_report_ids[-1], unique_report_ids[-1] - 1, unique_report_ids[-1] - 2]
    unloaded_reports_objs: list = []

    for value in for_delete_report_ids:
        if value in unique_report_ids:
            unloaded_reports_objs.append(handle_unload_report_obj(current_api_key, value))
            unique_report_ids.remove(value)

    UnloadedReports.objects.bulk_create(unloaded_reports_objs)
    handled_response_data['status'] = wildberries_response.get('status')
    handled_response_data['data'] = [
        sale for sale in wildberries_response.get(
            'data'
        ) if sale.get('realizationreport_id') in unique_report_ids]

    return handled_response_data


def get_wildberries_response_data(date_from: str, date_to: str, current_api_key):
    response = send_request_for_sales(date_from, date_to, current_api_key)

    if not response.get('status') or len(response.get('data')) < 100000:
        return response

    changed_response = get_wb_request_response(response, current_api_key)

    return changed_response

