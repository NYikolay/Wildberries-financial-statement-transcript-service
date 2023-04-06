import datetime
import json

from typing import List

from django.db.models import Q

from reports.services.report_generation_services.generate_priod_filters_services import \
    generate_period_filter_conditions
from reports.services.report_generation_services.generating_abc_xyz_report_services import get_abc_xyz_report
from reports.services.report_generation_services.generating_report_db_data_service import get_report_db_inter_data
from reports.services.report_generation_services.generating_share_in_revenue_by_filter_service import \
    get_share_in_revenue
from reports.services.report_generation_services.generating_sum_aggregation_objs_service import get_aggregate_sum_dicts
from reports.services.report_generation_services.get_total_financials_service import get_total_financials
from reports.services.report_generation_services.handling_calculated_finfancials_by_products_service import \
    get_calculated_financials_by_products


def get_abc(count, data):
    ara = data
    new_ara = []
    new_new_ara = {
        "A": {
            "revenue": 0,
            "share": 0
        },
        "B": {
            "revenue": 0,
            "share": 0
        },
        "C": {
            "revenue": 0,
            "share": 0
        }
    }

    lst = 0
    data.sort(key=lambda x: x['share_in_profits'], reverse=True)
    for value in ara:
        new_ara.append({
            "nm_id": value.get("nm_id"),
            "revenue": value.get("revenue_by_article"),
            "share": value.get("share_in_profits"),
            "b": value.get("share_in_profits") if len(new_ara) == 0 else value.get("share_in_profits") + new_ara[-1].get("b"),
            "c": (1 / count) * 100
        })

    for value in new_ara:
        if value.get("b") <= 80:
            value['group'] = 'A'
        elif 80 < value.get("b") <= 95:
            value['group'] = 'B'
        else:
            value['group'] = 'C'

    for value in new_ara:
        new_new_ara.get(value.get("group"))["revenue"] += value.get("revenue")
        new_new_ara.get(value.get("group"))["share"] += value.get("c")

    print(new_new_ara)


def get_full_user_report(current_user, current_api_key, period_filter_data: List[dict]) -> dict:
    """
    The function generates the final set of data sent to the view
    :param current_user: Current authorized user
    :param current_api_key: The user's current active WBApiKey
    :param period_filter_data: It can be empty.
    A list containing a dictionary with year (List[int]) and week_nums (List[int]) as keys.
    :return: Dictionary with calculated data
    """
    filter_period_conditions = generate_period_filter_conditions(period_filter_data)
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()

    report_intermediate_data = get_report_db_inter_data(
        current_user, current_api_key, filter_period_conditions, general_dict_aggregation_objs
    )

    totals: dict = get_total_financials(
        report_intermediate_data.get('sale_objects_by_weeks'),
        report_intermediate_data.get('supplier_costs_sum_list'),
        report_intermediate_data.get('wb_costs_sum_list'),
    )

    products_financials: list = [
        get_calculated_financials_by_products
        (sale, totals.get('revenue_total')) for sale in report_intermediate_data.get('sale_objects_by_products')]

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
        'report_by_products': json.dumps(products_financials),
        'is_empty_reports_values': report_intermediate_data.get('is_empty_reports_values'),
        'is_empty_netcosts_values': report_intermediate_data.get('is_empty_netcosts_values'),
        'is_exists_tax_values': report_intermediate_data.get('is_exists_tax_values'),
        'brands_share_in_revenue_dict': json.dumps(brands_share_in_revenue_dict, ensure_ascii=False),
        'stocks_share_in_revenue_dict': json.dumps(stocks_share_in_revenue_dict, ensure_ascii=False)
    }




