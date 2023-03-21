import logging
from datetime import datetime
from typing import List
import pytz

from django.db import transaction
from users.models import SaleObject, SaleReport, UnloadedReports, ClientUniqueProduct
from users.services.wb_request_hanling_services.generating_unique_reports import get_unique_reports

from users.services.wb_request_hanling_services.generating_user_reports import generate_reports
from users.services.wb_request_hanling_services.generating_incorrect_reports import generate_incorrect_reports
from users.services.wb_request_hanling_services.generating_user_products_objs import generate_user_products
from users.services.wb_request_hanling_services.reports_validation import get_incorrect_reports_lst
from users.services.wb_request_hanling_services.send_request_for_sales import send_request_for_sales, \
    get_wb_request_response

django_logger = logging.getLogger('django_logger')


def get_unique_articles(sales: list) -> list:
    articles_data: List[dict] = []
    for sale in sales:
        articles_nm_ids: List[int] = [i.get('nm_id') for i in articles_data]
        if sale.get('nm_id') not in articles_nm_ids and sale.get('nm_id'):
            articles_data.append(
                {
                    'nm_id': sale.get('nm_id'),
                    'brand': sale.get('brand_name')
                }
            )
    return articles_data


def handle_sale_obj(current_user, sale_obj: dict, api_key, current_product_objs):
    """
    The function generates an instance of the SaleObject class.
    IMPORTANT: Such values as: date_from, date_to, create_dt, order_dt, sale_dt
    do not check for None, because they are pre-checked by get_incorrect_reports_lst function
    :param current_user:
    :param sale_obj: Dictionary containing sales data
    :param api_key: WBApiKey object of the current user
    :param current_product_objs:
    :return:
    """
    wb_office_name = sale_obj.get('office_name')
    office_name = 'Склад WB без названия' if wb_office_name is None else wb_office_name
    week_num = datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').isocalendar()[1]
    year = datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').year
    month_num = datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').month
    date_from = datetime.strptime(
        sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    date_to = datetime.strptime(
        sale_obj.get('date_to'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    create_dt = datetime.strptime(
        sale_obj.get('create_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    order_dt = datetime.strptime(
        sale_obj.get('order_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    sale_dt = datetime.strptime(
        sale_obj.get('sale_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    rr_dt = None if not sale_obj.get('rr_dt') else datetime.strptime(
        sale_obj.get('rr_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))

    return SaleObject(
        owner=current_user,
        api_key=api_key,
        week_num=week_num,
        product=current_product_objs.get(sale_obj.get('nm_id')),
        year=year,
        month_num=month_num,
        realizationreport_id=sale_obj.get('realizationreport_id'),
        date_from=date_from,
        date_to=date_to,
        create_dt=create_dt,
        gi_id=sale_obj.get('gi_id'),
        subject_name=sale_obj.get('subject_name'),
        nm_id=sale_obj.get('nm_id'),
        brand_name=sale_obj.get('brand_name'),
        sa_name=sale_obj.get('sa_name'),
        ts_name=sale_obj.get('ts_name'),
        barcode=sale_obj.get('barcode'),
        doc_type_name=sale_obj.get('doc_type_name'),
        order_dt=order_dt,
        sale_dt=sale_dt,
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
        rrd_id=sale_obj.get('rrd_id'),
        retail_amount=sale_obj.get('retail_amount'),
        sale_percent=sale_obj.get('sale_percent'),
        commission_percent=sale_obj.get('commission_percent'),
        rr_dt=rr_dt,
        shk_id=sale_obj.get('shk_id'),
        delivery_amount=sale_obj.get('delivery_amount'),
        return_amount=sale_obj.get('return_amount'),
        gi_box_type_name=sale_obj.get('gi_box_type_name'),
        product_discount_for_report=sale_obj.get('product_discount_for_report'),
        supplier_promo=sale_obj.get('supplier_promo'),
        ppvz_spp_prc=sale_obj.get('ppvz_spp_prc'),
        ppvz_kvw_prc_base=sale_obj.get('ppvz_kvw_prc_base'),
        ppvz_kvw_prc=sale_obj.get('ppvz_kvw_prc'),
        ppvz_sales_commission=sale_obj.get('ppvz_sales_commission'),
        ppvz_reward=sale_obj.get('ppvz_reward'),
        acquiring_fee=sale_obj.get('acquiring_fee'),
        acquiring_bank=sale_obj.get('acquiring_bank'),
        ppvz_vw=sale_obj.get('ppvz_vw'),
        ppvz_vw_nds=sale_obj.get('ppvz_vw_nds'),
        ppvz_office_id=sale_obj.get('ppvz_office_id'),
        ppvz_office_name=sale_obj.get('ppvz_office_name'),
        ppvz_supplier_id=sale_obj.get('ppvz_supplier_id'),
        ppvz_supplier_name=sale_obj.get('ppvz_supplier_name'),
        ppvz_inn=sale_obj.get('ppvz_inn'),
        declaration_number=sale_obj.get('declaration_number'),
        bonus_type_name=sale_obj.get('bonus_type_name'),
        sticker_id=sale_obj.get('sticker_id'),
        kiz=sale_obj.get('kiz')
        )


def generate_reports_and_sales_objs(current_user, date_from: str, date_to, current_api_key) -> dict:
    """
    The main function of requesting data from Wildberries. Combines all services related to data uploading.
    Checks for piracy, generates a list of SaleObject models instances.
    :param current_user:
    :param date_from: date for sending a request to WIldberries in query params
    :param date_to: date for sending a request to WIldberries in query params
    :param current_api_key: WBApiKey object of the current user
    :return: Return the status of all functions that work with data from Wildberries in the view.
    """

    res_dict: dict = get_wb_request_response(date_from, date_to, current_api_key)

    if res_dict.get('status') is False:
        return res_dict

    if not res_dict.get('data'):
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }

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
    sale_obj_list: list = []

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
        for sale_obj in res_dict.get('data'):
            if sale_obj.get('realizationreport_id') in generated_reports_ids \
                    or sale_obj.get('realizationreport_id') in incorrect_reports.get('realizationreport_ids'):
                continue
            sale_obj_list.append(handle_sale_obj(current_user, sale_obj, current_api_key, current_product_objs))
    except Exception as err:
        django_logger.critical(f'Error when creating sale objects {current_user.email}.'
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

            generate_incorrect_reports(
                current_user,
                incorrect_reports.get('incorrect_reports_data_list'),
                current_api_key
            )
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
