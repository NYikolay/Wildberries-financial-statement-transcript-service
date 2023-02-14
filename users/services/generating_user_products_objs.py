import logging
from threading import Thread
from time import sleep

from django.db import transaction
from django.core.cache import cache
from django.core.exceptions import RequestAborted

from users.models import ClientUniqueProduct
from users.services.generate_unique_articles_obj import handle_unique_articles
from users.services.generating_user_products_data import get_article_additional_data


django_logger = logging.getLogger('django_logger')


def generate_user_products(request, unique_articles, current_api_key) -> None:
    current_user = request.user
    unique_articles_len_counter: int = len(unique_articles)

    unique_articles_values = []
    article_obj_list = []

    for article in unique_articles:
        if ClientUniqueProduct.objects.filter(api_key__user=current_user,
                                              api_key=current_api_key,
                                              nm_id=article.get('nm_id')).exists():
            unique_articles_len_counter -= 1
            continue

        thread = Thread(
            target=get_article_additional_data,
            args=(article.get('nm_id'), article.get('brand'), unique_articles_values),
            daemon=True
        )
        thread.start()

    cnt = 0
    while len(unique_articles_values) != unique_articles_len_counter:
        sleep(0.5)
        cnt += 1
        if cnt > len(unique_articles):
            django_logger.critical(
                f'Sales reports were not loaded for the user {current_user.email} due to an error during the '
                f'loading of products and their pictures. Problems with threading'
            )
            raise RequestAborted

    for article_data in unique_articles_values:
        article_obj_list.append(handle_unique_articles(article_data, current_api_key))

    try:
        with transaction.atomic():

            ClientUniqueProduct.objects.bulk_create(article_obj_list)

            if not current_api_key.is_products_loaded:
                current_api_key.is_products_loaded = True
                current_api_key.save()

    except Exception as err:
        django_logger.critical(
            f'Failed to create product objects for a user - {current_user.email}',
            exc_info=err
        )
