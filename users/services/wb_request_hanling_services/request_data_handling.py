import logging
from datetime import datetime, timezone
from typing import List, Set

from django.db import transaction
from users.models import SaleObject, SaleReport

from users.services.wb_request_hanling_services.generating_user_reports import generate_reports
from users.services.wb_request_hanling_services.generating_incorrect_reports import generate_incorrect_reports
from users.services.wb_request_hanling_services.generating_user_products_objs import generate_user_products
from users.services.wb_request_hanling_services.reports_validation import get_incorrect_reports_lst
from users.services.wb_request_hanling_services.send_request_for_sales import send_request_for_sales

django_logger = logging.getLogger('django_logger')


def get_unique_articles(sales: list) -> list:
    articles_data: List[dict] = []
    for sale in sales:
        articles_nm_ids: List[int] = [i.get('nm_id') for i in articles_data]
        if sale.get('nm_id') not in articles_nm_ids and sale.get('nm_id') is not None:
            articles_data.append(
                {
                    'nm_id': sale.get('nm_id'),
                    'brand': sale.get('brand_name')
                }
            )
    return articles_data


def get_unique_reports(sales: list) -> set:
    reports_data: Set[int] = set()
    for sale in sales:
        reports_data.add(sale.get('realizationreport_id'))
    return reports_data


def handle_sale_obj(request, sale_obj: dict, api_key):
    wb_office_name = sale_obj.get('office_name', None)
    office_name = 'Склад WB без названия' if wb_office_name is None else wb_office_name

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
        office_name=office_name,
        srid=sale_obj.get('srid'),
        delivery_rub=sale_obj.get('delivery_rub'),
        rid=sale_obj.get('rid'),
        supplier_oper_name=sale_obj.get('supplier_oper_name'),
        )


def generate_reports_and_sales_objs(request, date_from: str, date_to: str, current_api_key) -> dict:
    """
    The main function of requesting data from Wildberries. Combines all services related to data uploading.
    Checks for piracy, generates a list of SaleObject model instances.
    :param request:
    :param date_from:
    :param date_to:
    :param current_api_key:
    :return: Return the results of all functions that work with data from Wildberries in the view.
    """

    res_dict = send_request_for_sales(date_from, date_to, current_api_key)

    if res_dict is None:
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }

    incorrect_reports: dict = get_incorrect_reports_lst(res_dict)
    unique_articles: list = get_unique_articles(res_dict)
    unique_reports_ids: set = get_unique_reports(res_dict)

    if SaleReport.objects.filter(realizationreport_id__in=unique_reports_ids).exclude(owner=request.user).exists():
        django_logger.info(
            f"Attempted piracy, user - {request.user.email} "
            f"tries to upload someone else's reports or another account's reports"
        )
        return {
            'status': False,
            'message': 'Отчёты принадлежат другому пользователю.'
        }

    sale_obj_list: list = []

    generated_reports_ids = SaleReport.objects.filter(
        owner=request.user,
        api_key=current_api_key
    ).values_list('realizationreport_id', flat=True)

    try:
        for sale_obj in res_dict:
            if sale_obj.get('realizationreport_id') in generated_reports_ids \
                    or sale_obj.get('realizationreport_id') in incorrect_reports.get('realizationreport_ids'):
                continue
            sale_obj_list.append(handle_sale_obj(request, sale_obj, current_api_key))
    except Exception as err:
        django_logger.critical(f'Error when creating sale objects {request.user.email}.'
                               f'An error on the Wildberries side that blocks the loading of reports', exc_info=err)
        return {
            'status': False,
            'message': 'Нестабильная работа Wildberries. Пожалуйста, попробуйте позже.'
        }

    if len(sale_obj_list) == 0:
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }

    try:
        with transaction.atomic():
            SaleObject.objects.bulk_create(sale_obj_list, batch_size=5000)

            generate_incorrect_reports(request, incorrect_reports.get('incorrect_reports_data_list'), current_api_key)
            generate_reports(request, current_api_key)
            generate_user_products(request, unique_articles, current_api_key)
    except Exception as err:
        django_logger.critical(
            f'Failed to load reports into the database for a user {request.user.email}',
            exc_info=err
        )
        return {
            'status': False,
            'message': 'Произошла ошибка во время загрузки отчёта. Не удалось сохранить данные.'
        }

    return {
        'status': True
    }