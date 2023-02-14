import json
import logging

import requests
from fake_headers import Headers

django_logger = logging.getLogger('django_logger')


def send_request_for_card_json(url: str, article: int) -> str or None:
    headers = Headers(os="chrome", headers=True).generate()

    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        django_logger.error(
            f'Blocking when loading images or the link generation algorithm is outdated. Article - {article}',
        )

        return f'Товар с артикулом {article}'

    return json.loads(response.text).get('imt_name')


def get_article_additional_data(article: int, brand: str, article_obj_list: list) -> None:
    small_article_1: int = article // 100000
    small_article_2: int = article // 1000

    links_conditions_data = {
        143 >= small_article_1 >= 0: '//basket-01.wb.ru/',
        287 >= small_article_1 >= 144: '//basket-02.wb.ru/',
        431 >= small_article_1 >= 288: '//basket-03.wb.ru/',
        719 >= small_article_1 >= 432: '//basket-04.wb.ru/',
        1007 >= small_article_1 >= 720: '//basket-05.wb.ru/',
        1061 >= small_article_1 >= 1008: '//basket-06.wb.ru/',
        1115 >= small_article_1 >= 1062: '//basket-07.wb.ru/',
        1169 >= small_article_1 >= 1116: '//basket-08.wb.ru/',
        1313 >= small_article_1 >= 1170: '//basket-09.wb.ru/',
        1601 >= small_article_1 >= 1314: '//basket-10.wb.ru/',
        1889 >= small_article_1 >= 1602: '//basket-11.wb.ru/',
    }

    basket_url: str = links_conditions_data.get(True, '//basket-12.wb.ru/')

    json_data_url: str = f'https:{basket_url}/vol{small_article_1}/part{small_article_2}/{article}/info/ru/card.json'
    img_url: str = f'https://{basket_url}/vol{small_article_1}/part{small_article_2}/{article}/images/tm/1.jpg'

    product_name = send_request_for_card_json(json_data_url, article)

    article_obj_list.append({
        'title': product_name,
        'img': img_url,
        'nm_id': article,
        'brand': brand,
    })
