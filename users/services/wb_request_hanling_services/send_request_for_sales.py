from users.services.decrypt_api_key import get_decrypted_key
import requests


def send_request_for_sales(date_from: str, date_to: str, current_api_key) -> list or dict:

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
                       'Пожалуйста, введите верный ключ или повторите попытку.'
        }
    elif response.status_code != 200:
        return {
            'status': False,
            'message': 'Ошибка при попытке получения данных от Wildberries. Пожалуйста, попробуйте позже.'
        }

    return response.json()
