import json
from typing import List, Union
from django.db import connection
from django.db.models import (
    Sum, Q, FloatField, F, QuerySet)
from django.db.models.functions import Coalesce
from reports.services.report_generation_services.generate_period_filters_services import \
    generate_period_filter_conditions
from reports.services.report_generation_services.generating_financials_by_barcodes import \
    get_calculated_financials_by_barcodes
from reports.services.report_generation_services.generating_report_db_data_services import get_report_db_inter_data, \
    get_sale_objects_by_barcode_by_weeks, get_products_count_by_period, get_total_revenue, \
    get_calculated_financials_by_products, get_penalties
from reports.services.report_generation_services.generating_share_in_revenue_by_filter_service import \
    get_share_in_revenue
from reports.services.report_generation_services.generating_sum_aggregation_objs_services import \
    get_aggregate_sum_dicts, get_financials_annotation_objects, get_product_financials_annotations_objects
from reports.services.report_generation_services.get_totals_by_barcode import \
    get_total_financials_by_barcode
from reports.services.report_generation_services.get_total_financials_service import get_total_financials
from users.models import SaleObject


def get_full_user_report(current_user, current_api_key, period_filter_data: List[dict]) -> dict:
    """
    The function generates the final set of data sent to the view
    :param current_user: Current authorized user
    :param current_api_key: The user's current active WBApiKey
    :param period_filter_data: It can be empty.
    A list containing a dictionary with year (List[int]) and week_nums (List[int]) as keys.
    :return: Dictionary with calculated data
    """
    filter_period_conditions: dict = generate_period_filter_conditions(period_filter_data)
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()

    report_intermediate_data = get_report_db_inter_data(
        current_user, current_api_key, filter_period_conditions, general_dict_aggregation_objs
    )

    totals: dict = get_total_financials(
        report_intermediate_data.get('sale_objects_by_weeks'),
        report_intermediate_data.get('supplier_costs_sum_list'),
        report_intermediate_data.get('wb_costs_sum_list'),
    )

    brands_share_in_revenue_dict: dict = get_share_in_revenue(
        current_user, current_api_key, filter_period_conditions, totals.get('revenue_total'), 'brand_name')
    stocks_share_in_revenue_dict: dict = get_share_in_revenue(
        current_user, current_api_key, filter_period_conditions, totals.get('revenue_total'), 'office_name')
    category_share_in_revenue_dict: dict = get_share_in_revenue(
        current_user, current_api_key, filter_period_conditions, totals.get('revenue_total'), 'subject_name')

    penalties = get_penalties(current_user, current_api_key, filter_period_conditions)

    return {
        **totals,
        'brands_share_in_revenue_dict': json.dumps(brands_share_in_revenue_dict, ensure_ascii=False),
        'stocks_share_in_revenue_dict': json.dumps(stocks_share_in_revenue_dict, ensure_ascii=False),
        'category_share_in_revenue_dict': json.dumps(category_share_in_revenue_dict, ensure_ascii=False),
        'penalties': penalties
    }


def get_report_by_barcodes(
        current_user,
        current_api_key,
        period_filter_data: List[dict],
        convert_products_data_to_json: bool = False
):
    filter_period_conditions: dict = generate_period_filter_conditions(period_filter_data)
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()
    financials_annotations_objs: dict = get_financials_annotation_objects()

    with connection.cursor() as cursor:
        sql = "SET JIT = OFF;"
        cursor.execute(sql)

    total_revenue = get_total_revenue(
        current_user,
        current_api_key,
        filter_period_conditions,
        general_dict_aggregation_objs.get('sum_aggregation_objs_dict')
    )

    products_count_by_period = get_products_count_by_period(
        current_user,
        current_api_key,
        filter_period_conditions
    )

    report_by_barcodes = get_calculated_financials_by_barcodes(
        current_user, current_api_key, filter_period_conditions,
        general_dict_aggregation_objs.get('sum_aggregation_objs_dict'),
        general_dict_aggregation_objs.get('net_costs_sum_aggregation_objs'),
        total_revenue.get('total_revenue'),
        products_count_by_period,
        financials_annotations_objs,
        convert_products_data_to_json
    )

    return report_by_barcodes


def get_report_by_barcode(current_user, current_api_key, period_filter_data: List[dict], barcode):
    filter_period_conditions: dict = generate_period_filter_conditions(period_filter_data)
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()
    annotations_objs: dict = get_product_financials_annotations_objects()

    with connection.cursor() as cursor:
        sql = "SET JIT = OFF;"
        cursor.execute(sql)

    products_by_barcodes = SaleObject.objects.filter(
        ~Q(nm_id=99866376),
        owner=current_user,
        api_key=current_api_key,
        nm_id__isnull=False,
    ).distinct('barcode', 'ts_name', 'nm_id').order_by('barcode').annotate(
        image=F('product__image'),
        product_name=F('product__product_name')
    ).values('nm_id', 'barcode', 'ts_name', 'image', 'product_name')

    barcode_report_by_weeks: Union[QuerySet, List[dict]] = get_sale_objects_by_barcode_by_weeks(
        barcode,
        current_user,
        current_api_key,
        filter_period_conditions,
        general_dict_aggregation_objs.get('sum_aggregation_objs_dict'),
        general_dict_aggregation_objs.get('net_costs_sum_aggregation_objs'),
        annotations_objs,
    )

    totals: dict = get_total_financials_by_barcode(barcode_report_by_weeks)

    return {
        "totals": totals,
        "report_by_weeks": json.dumps(list(barcode_report_by_weeks), ensure_ascii=False),
        "products_by_barcodes": products_by_barcodes
    }





