import sys
from datetime import datetime, timedelta, date, timezone

from django.db import transaction

from users.models import WBApiKey, SaleObject, SaleReport
from users.services.decrypt_api_key import get_decrypted_key
from users.services.generate_user_reports import generate_reports

import requests


def get_api_key(api_key_obj) -> str:
    api_key = get_decrypted_key(api_key_obj.api_key)

    return api_key


def get_unique_articles(sales: list) -> list:
    articles_data = []
    for sale in sales:
        articles_nm_ids = [i.get('nm_id') for i in articles_data]
        if sale.get('nm_id') not in articles_nm_ids:
            articles_data.append(
                {
                    'nm_id': sale.get('nm_id'),
                    'brand': sale.get('brand_name')
                }
            )
    return articles_data


def get_unique_reports(sales: list) -> list:
    reports_data = []
    for sale in sales:
        if sale.get('realizationreport_id') not in reports_data:
            reports_data.append(sale.get('realizationreport_id'))
    return reports_data


def handle_sale_obj(request, sale_obj: dict, api_key):
    return SaleObject(
        owner=request.user,
        api_key=api_key,
        week_num=
        datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').
        replace(tzinfo=timezone.utc).isocalendar()[1],
        year=datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').
        replace(tzinfo=timezone.utc).year,
        month_num=datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').
        replace(tzinfo=timezone.utc).month,
        realizationreport_id=sale_obj.get('realizationreport_id'),
        date_from=datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
        date_to=datetime.strptime(sale_obj.get('date_to'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
        create_dt=datetime.strptime(sale_obj.get('create_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
        gi_id=sale_obj.get('gi_id'),
        subject_name=sale_obj.get('subject_name'),
        nm_id=sale_obj.get('nm_id'),
        brand_name=sale_obj.get('brand_name'),
        sa_name=sale_obj.get('sa_name'),
        ts_name=sale_obj.get('ts_name'),
        barcode=sale_obj.get('barcode'),
        doc_type_name=sale_obj.get('doc_type_name'),
        order_dt=datetime.strptime(sale_obj.get('order_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
        sale_dt=datetime.strptime(sale_obj.get('sale_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
        quantity=sale_obj.get('quantity'),
        retail_price=sale_obj.get('retail_price'),
        retail_price_withdisc_rub=sale_obj.get('retail_price_withdisc_rub'),
        ppvz_for_pay=sale_obj.get('ppvz_for_pay'),
        penalty=sale_obj.get('penalty'),
        additional_payment=sale_obj.get('additional_payment'),
        site_country=sale_obj.get('site_country'),
        office_name=sale_obj.get('office_name', 'Склад WB без названия'),
        srid=sale_obj.get('srid'),
        delivery_rub=sale_obj.get('delivery_rub'),
        rid=sale_obj.get('rid'),
        supplier_oper_name=sale_obj.get('supplier_oper_name'),
        )


def generate_reports_and_sales_objs(request, date_from, date_to, current_api_key):

    headers = {
        'Authorization': get_api_key(current_api_key)
    }

    query = {
        "dateFrom": date_from,
        "dateTo": date_to,
    }

    r = requests.get('https://statistics-api.wildberries.ru/api/v1/supplier/reportDetailByPeriod', headers=headers,
                     params=query)

    if r.status_code == 401:
        return {
            'status': False,
            'message': 'Wildberries не может распознать текущий API ключ. '
                       'Пожалуйста, введите верный ключ или повторите попытку.'
        }
    elif r.status_code != 200:
        return {
            'status': False,
            'message': 'Ошибка при попытке получения данных от Wildberries. Пожалуйста, попробуйте позже.'
        }

    res_dict = r.json()

    if res_dict is None:
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые отчёты за текущую дату.'
        }

    unique_articles = get_unique_articles(res_dict)
    unique_reports_id_list = get_unique_reports(res_dict)
    sale_obj_list = []

    if SaleReport.objects.filter(realizationreport_id__in=unique_reports_id_list).exclude(owner=request.user).exists():
        return {
            'status': False,
            'message': 'Отчёты принадлежат другому пользователю.'
        }

    reports_ids = SaleReport.objects.filter(
        owner=request.user,
        api_key=current_api_key
    ).values_list('realizationreport_id', flat=True)

    try:
        for sale_obj in res_dict:
            if sale_obj.get('realizationreport_id') in reports_ids:
                continue
            sale_obj_list.append(handle_sale_obj(request, sale_obj, current_api_key))
    except Exception as err:
        return {
            'status': False,
            'message': 'Нестабильная работа Wildberries. Пожалуйста, попробуйте позже.'
        }

    try:

        with transaction.atomic():

            SaleObject.objects.bulk_create(sale_obj_list)

            generate_reports(request, current_api_key)

    except Exception as err:
        return {
            'status': False,
            'message': 'Произошла ошибка во время загрузки отчёта. Не удалось сохранить данные.'
        }

    return {
        'status': True,
        'unique_articles': unique_articles
    }
