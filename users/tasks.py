from django.core.mail import EmailMessage
from django.db import transaction
from django.core.cache import cache


from celery import shared_task
from selenium.common.exceptions import TimeoutException

from config.settings.base import EMAIL_HOST_USER
from users.models import ClientUniqueProduct, User, WBApiKey
from users.services.generate_unique_articles_obj import handle_unique_articles
from users.services.scraping_product_data import get_scraping_data
from users.token import account_activation_token


@shared_task()
def generate_user_products(user_id: int, unique_articles: list, api_key_id):
    current_user = User.objects.get(id=user_id)
    current_api_key = WBApiKey.objects.get(id=api_key_id, user=current_user, is_current=True)
    unique_articles_values = []

    article_obj_list = []
    for article in unique_articles:
        if ClientUniqueProduct.objects.filter(api_key__user=current_user,
                                              api_key=current_api_key,
                                              nm_id=article.get('nm_id')).exists():
            continue

        try:
            unique_articles_values.append(get_scraping_data(article.get('nm_id'), article.get('brand')))
        except TimeoutException as ex:
            unique_articles_values.append({
                'img': None,
                'nm_id': article.get('nm_id'),
                'brand': article.get('brand'),
                'title': f'Товар с артикулом {article.get("nm_id")}'
            })

    for article_data in unique_articles_values:
        article_obj_list.append(handle_unique_articles(article_data, current_api_key))

    try:
        with transaction.atomic():

            ClientUniqueProduct.objects.bulk_create(article_obj_list)

            if not current_api_key.is_products_loaded:
                current_api_key.is_products_loaded = True
                current_api_key.save()

    except Exception:
        ...

    cache.delete('report_cache')


@shared_task()
def send_email_verification(mail_message, to_email, mail_subject):

    to_email = to_email

    email = EmailMessage(
        mail_subject, mail_message, to=[to_email], from_email=EMAIL_HOST_USER
    )
    email.send()

