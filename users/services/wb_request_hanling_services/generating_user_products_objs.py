import logging
from threading import Thread
from time import sleep

from django.db import transaction
from django.core.exceptions import RequestAborted

from users.models import ClientUniqueProduct
from users.services.wb_request_hanling_services.generating_user_products_data import handle_article_additional_data


django_logger = logging.getLogger('django_logger')


def handle_unique_articles(article_values: dict, api_key):
    return ClientUniqueProduct(
        api_key=api_key,
        nm_id=article_values.get('nm_id', 0),
        brand=article_values.get('brand'),
        image=article_values.get('img', 'https://None.ru'),
        product_name=article_values.get('title', 'None')
    )


def generate_user_products(current_user, unique_articles: list, current_api_key) -> None:
    """
    A function that generates and creates instances of the table ClientUniqueProduct in the database.
    Product processing is performed in multi-threaded mode
    :param current_user:
    :param unique_articles: unique request user product identifiers received
    when loading the report and passed the validation
    :param current_api_key: current WBApiKey of request user
    :return:
    """

    unique_articles_len_counter: int = len(unique_articles)

    unique_articles_values: list = []
    article_obj_list: list = []

    for article in unique_articles:
        if ClientUniqueProduct.objects.filter(api_key__user=current_user,
                                              api_key=current_api_key,
                                              nm_id=article.get('nm_id')).exists():
            unique_articles_len_counter -= 1
            continue

        thread = Thread(
            target=handle_article_additional_data,
            args=(article.get('nm_id'), article.get('brand'), unique_articles_values),
            daemon=True
        )
        thread.start()

    cnt: int = 0
    while len(unique_articles_values) != unique_articles_len_counter:
        sleep(0.2)
        cnt += 1
        if cnt > len(unique_articles):
            django_logger.critical(
                f'Sales reports were not loaded for the user {current_user.email} due to an error during the '
                f'loading of products and their pictures. Problems with threading'
            )
            raise RequestAborted

    for article_data in unique_articles_values:
        article_obj_list.append(handle_unique_articles(article_data, current_api_key))

    with transaction.atomic():

        ClientUniqueProduct.objects.bulk_create(article_obj_list)

        if not current_api_key.is_products_loaded:
            current_api_key.is_products_loaded = True
            current_api_key.save()