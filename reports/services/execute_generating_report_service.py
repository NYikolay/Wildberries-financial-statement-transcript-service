import json
from typing import List

from reports.services.report_generation_services.generate_period_filters_services import \
    generate_period_filter_conditions
from reports.services.report_generation_services.generating_abc_xyz_report_services import get_abc_xyz_report
from reports.services.report_generation_services.generating_report_db_data_services import get_report_db_inter_data, \
    get_sale_objects_by_barcode_by_weeks
from reports.services.report_generation_services.generating_share_in_revenue_by_filter_service import \
    get_share_in_revenue
from reports.services.report_generation_services.generating_sum_aggregation_objs_service import get_aggregate_sum_dicts
from reports.services.report_generation_services.get_financials_by_barcode_services import \
    get_total_financials_by_barcode
from reports.services.report_generation_services.get_total_financials_service import get_total_financials


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

    abc_xyz = get_abc_xyz_report(
        current_user, current_api_key, filter_period_conditions,
        general_dict_aggregation_objs.get('sum_aggregation_objs_dict'),
        general_dict_aggregation_objs.get('net_costs_sum_aggregation_objs'),
        totals.get('revenue_total'),
        report_intermediate_data.get('products_count_by_period')
    )

    return {
        **totals,
        'is_empty_reports_values': report_intermediate_data.get('is_empty_reports_values'),
        'is_empty_netcosts_values': report_intermediate_data.get('is_empty_netcosts_values'),
        'is_exists_tax_values': report_intermediate_data.get('is_exists_tax_values'),
        'brands_share_in_revenue_dict': json.dumps(brands_share_in_revenue_dict, ensure_ascii=False),
        'stocks_share_in_revenue_dict': json.dumps(stocks_share_in_revenue_dict, ensure_ascii=False),
        'products_calculated_values': json.dumps(abc_xyz.get('products_calculated_values')),
        'abc_report': abc_xyz.get('abc_report'),
        'abc_xyz_report': abc_xyz.get('abc_xyz_report'),
    }


def get_report_by_barcode(current_user, current_api_key, period_filter_data: List[dict], barcode, nm_id):
    filter_period_conditions: dict = generate_period_filter_conditions(period_filter_data)
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()

    sale_objects_by_weeks = get_sale_objects_by_barcode_by_weeks(
        current_user, current_api_key, filter_period_conditions,
        general_dict_aggregation_objs.get('sum_aggregation_objs_dict'),
        general_dict_aggregation_objs.get('net_costs_sum_aggregation_objs'), barcode, nm_id)

    totals = get_total_financials_by_barcode(sale_objects_by_weeks)

    return totals






