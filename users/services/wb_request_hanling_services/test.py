import datetime

from users.models import UnloadedReports, SaleReport, ClientUniqueProduct, IncorrectReport, SaleObject
import logging

from users.services.wb_request_hanling_services.generating_products_objs_service import generate_user_products
from users.services.wb_request_hanling_services.generating_sale_objects_service import handle_sale_obj
from users.services.wb_request_hanling_services.generating_user_reports_service import generate_reports
from users.services.wb_request_hanling_services.wildberries_request_handling_service import send_request_for_sales
from django.db import transaction
import pandas as pd
import timeit

django_logger = logging.getLogger('django_logger')


def get_unloaded_report_object(current_api_key, realizationreport_id):
    return UnloadedReports(api_key=current_api_key, realizationreport_id=realizationreport_id)


def get_incorrect_report_obj(current_user, report_data: dict, current_api_key):
    return IncorrectReport(
        api_key=current_api_key,
        owner=current_user,
        realizationreport_id=report_data.get('realizationreport_id'),
        date_from=report_data.get('date_from'),
        date_to=report_data.get('date_to')
    )


def create_unloaded_report_objects(current_api_key, realizationreport_ids):

    UnloadedReports.objects.bulk_create(
        [get_unloaded_report_object(current_api_key, report_id) for report_id in realizationreport_ids]
    )


def create_incorrect_reports(current_user, current_api_key, incorrect_reports):
    if not incorrect_reports.empty:
        IncorrectReport.objects.filter(owner=current_user, api_key=current_api_key).delete()
        return None

    generated_incorrect_reports = IncorrectReport.objects.filter(
        owner=current_user,
        api_key=current_api_key
    ).values_list('realizationreport_id', flat=True)

    try:
        reports_to_create = [get_incorrect_report_obj(current_user, row, current_api_key)
                             for index, row in incorrect_reports.iterrows()
                             if row['realizationreport_id'] not in generated_incorrect_reports]
        IncorrectReport.objects.bulk_create(reports_to_create)
    except Exception as err:
        django_logger.error(
            f'Error during the loading of a broken report from a user - {current_user.email}',
            exc_info=err
        )
        transaction.rollback()


def create_sale_objects(
        current_user,
        current_api_key,
        data_frame,
        generated_reports_ids,
        incorrect_reports_ids,
        generated_products_objs
):
    sales_to_create = [
        handle_sale_obj(current_user, row, current_api_key, generated_products_objs)
        for index, row in data_frame.iterrows()
        if row['realizationreport_id'] not in generated_reports_ids
           and row['realizationreport_id'] not in incorrect_reports_ids
    ]

    if not sales_to_create:
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }

    SaleObject.objects.bulk_create(sales_to_create, batch_size=5000)

    return {'status': True}


def get_sorted_unique_report_ids(data_frame):
    # Getting the unique nm_ids as an array
    unique_ids = data_frame['realizationreport_id'].unique()

    # Sorting from lesser to greater
    unique_ids_sorted = pd.Series(unique_ids).sort_values().values

    return unique_ids_sorted


def get_unique_nm_ids(data_frame):
    """
    Get unique nm_ids from a DataFrame excluding None and 99866376 values.
    :param data_frame: Pandas DataFrame object
    :return: Array of unique nm_ids
    """

    # Filtering out the unwanted nm_id using query() method
    df = data_frame.query("nm_id != 99866376")

    # Dropping rows with null nm_id values
    df.dropna(subset=['nm_id'], inplace=True)

    # Getting the unique nm_ids as an array
    unique_nm_ids = df['nm_id'].unique()

    return unique_nm_ids


def get_filtered_wildberries_response(current_api_key, response):
    unique_report_ids = get_sorted_unique_report_ids(response)

    for_delete_report_ids = [unique_report_ids[-1], unique_report_ids[-1] - 1, unique_report_ids[-1] - 2]
    create_unloaded_report_objects(current_api_key, for_delete_report_ids)

    response = response.query('realizationreport_id not in @for_delete_report_ids')

    return response


def get_wildberries_response(current_api_key, date_from: str, date_to: str):
    dt = datetime.datetime.now()
    response = send_request_for_sales(date_from, date_to, current_api_key)
    print(f'Вб отдал за: {datetime.datetime.now() - dt}')

    if not response.get('status'):
        return response

    response_dataframe = pd.DataFrame(response['data'])

    if len(response['data']) < 100000:
        return response_dataframe

    filtered_response = get_filtered_wildberries_response(current_api_key, response_dataframe)

    return filtered_response


def check_additional_conditions(row):
    additional_condition_1 = [
        row.get('delivery_rub') is not None and row.get('delivery_rub') > 0,
        row.get('supplier_oper_name') == "Логистика",
        row.get('realizationreport_id') is not None,
        row.get('date_from') is not None,
        row.get('date_to') is not None,
        row.get('create_dt') is not None,
        row.get('subject_name') is None,
        row.get('nm_id') is None,
        row.get('brand_name') is None,
        row.get('barcode') is not None,
        row.get('doc_type_name') == 'Продажа',
        row.get('quantity') == 0,
        row.get('retail_price_withdisc_rub') == 0,
        row.get('ppvz_for_pay') == 0
    ]

    additional_condition_2 = [
        row.get('realizationreport_id') is not None,
        row.get('date_from') is not None,
        row.get('date_to') is not None,
        row.get('create_dt') is not None,
        row.get('subject_name') is not None,
        row.get('nm_id') is not None,
        row.get('ts_name') is not None,
        row.get('barcode') is not None,
        row.get('doc_type_name') is not None,
        row.get('brand_name') is None,
        row.get('quantity') is not None,
        row.get('retail_amount') is not None,
        row.get('supplier_oper_name') is not None,
        row.get('retail_price_withdisc_rub') is not None,
        row.get('delivery_rub') is not None,
        row.get('ppvz_for_pay') is not None
    ]

    additional_condition_3 = [
        row.get('supplier_oper_name') == 'Перевыставление расходов по логистике' or row.get(
            'supplier_oper_name') == 'Возмещение издержек по перевозке',
        row.get('order_dt') is None,
        row.get('sale_dt') is None,
        row.get('retail_price_withdisc_rub') is None,
        row.get('delivery_amount') is None,
        row.get('return_amount') is None,
        row.get('delivery_rub') is None,
        row.get('product_discount_for_report') is None,
        row.get('supplier_promo') is None,
        row.get('rid') is None,
        row.get('sticker_id') is None,
        row.get('site_country') is None,
        row.get('srid') is None
    ]

    if all(additional_condition_1) or all(additional_condition_2) or all(additional_condition_3):
        return True
    return False


def get_incorrect_reports(data_frame):
    column_names = [
        'date_from', 'realizationreport_id', 'date_to', 'create_dt', 'gi_id', 'subject_name',
        'nm_id', 'brand_name', 'ts_name', 'barcode', 'doc_type_name', 'order_dt', 'sale_dt', 'quantity',
        'retail_price', 'retail_price_withdisc_rub', 'ppvz_for_pay', 'penalty', 'additional_payment',
        'site_country', 'srid', 'delivery_rub', 'rid', 'supplier_oper_name', 'retail_amount'
    ]

    result_df = data_frame[
        data_frame.apply(lambda row: pd.isna(row[column_names]).any() and not check_additional_conditions(row), axis=1)]

    result_df = result_df[['realizationreport_id', 'date_from', 'date_to']]

    result_df = result_df.drop_duplicates(subset=['realizationreport_id'])

    return result_df


def execute_wildberries_request_data_handling_2(current_user, date_from: str, date_to, current_api_key):
    response = get_wildberries_response(current_api_key, date_from, date_to)

    if response.get('status') is False:
        return response
    dt = datetime.datetime.now()
    unique_reports_ids = get_sorted_unique_report_ids(response).tolist()
    unique_nm_ids = get_unique_nm_ids(response).tolist()
    incorrect_reports = get_incorrect_reports(response)
    print(f'Обработка датафреймов: {datetime.datetime.now() - dt}')

    if SaleReport.objects.filter(realizationreport_id__in=unique_reports_ids).exclude(owner=current_user).exists():
        django_logger.info(
            f"Attempted piracy, user - {current_user.email} "
            f"tries to upload someone else's reports or another account's reports"
        )
        return {
            'status': False,
            'message': 'Отчёты принадлежат другому пользователю.'
        }

    try:
        generate_user_products(current_user, set(unique_nm_ids), current_api_key)
    except Exception as err:
        django_logger.critical(
            f'Failed to create product objects for a user - {current_user.email}',
            exc_info=err
        )
        return {
            'status': False,
            'message': 'Произошла ошибка во время загрузки отчёта. Пожалуйста, обратитесь в службу поддержки.'
        }

    current_product_objs = ClientUniqueProduct.objects.in_bulk(unique_nm_ids, field_name='nm_id')

    generated_reports_ids = SaleReport.objects.filter(
        owner=current_user,
        api_key=current_api_key
    ).values_list('realizationreport_id', flat=True)

    try:
        with transaction.atomic():

            create_incorrect_reports(current_user, current_api_key, incorrect_reports)

            sale_objects_creating_status = create_sale_objects(
                current_user,
                current_api_key,
                response,
                generated_reports_ids,
                incorrect_reports['realizationreport_id'].values.tolist(),
                current_product_objs
            )

            if not sale_objects_creating_status.get('status'):
                return sale_objects_creating_status

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



