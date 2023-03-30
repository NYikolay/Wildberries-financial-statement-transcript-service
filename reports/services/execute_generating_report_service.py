
import json

from typing import List

from django.db.models import Q

from reports.services.report_generation_services.generating_report_db_data_service import get_report_db_inter_data
from reports.services.report_generation_services.generating_share_in_revenue_by_filter_service import \
    get_share_in_revenue
from reports.services.report_generation_services.get_total_financials_service import get_total_financials
from reports.services.report_generation_services.handling_calculated_finfancials_by_products_service import \
    get_calculated_financials_by_products


def generate_period_filter_conditions(period_filter_data: list):
    """
    The function forms an instance of the Q() class to filter
    :param period_filter_data: It can be empty.
    A list containing a dictionary with year (List[int]) and week_nums (List[int]) as keys.
    :return: An instance of class Q with data for filtering
    """
    empty_q_obj = Q()

    for filter_data in period_filter_data:
        empty_q_obj |= Q(year=filter_data.get('year'), week_num__in=filter_data.get('week_nums'))

    return empty_q_obj


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

    report_intermediate_data = get_report_db_inter_data(current_user, current_api_key, filter_period_conditions)

    totals: dict = get_total_financials(
        report_intermediate_data.get('sale_objects_by_weeks'),
        report_intermediate_data.get('supplier_costs_sum_list'),
        report_intermediate_data.get('wb_costs_sum_list')
    )

    products_financials: list = [
        get_calculated_financials_by_products
        (sale, totals.get('revenue_total')) for sale in report_intermediate_data.get('sale_objects_by_products')]

    brands_share_in_revenue_dict: dict = get_share_in_revenue(
        current_user, current_api_key, filter_period_conditions, totals.get('revenue_total'), 'brand_name')
    stocks_share_in_revenue_dict: dict = get_share_in_revenue(
        current_user, current_api_key, filter_period_conditions, totals.get('revenue_total'), 'office_name')

    return {
        **totals,
        'report_by_products': json.dumps(products_financials),
        'is_empty_reports_values': report_intermediate_data.get('is_empty_reports_values'),
        'is_empty_netcosts_values': report_intermediate_data.get('is_empty_netcosts_values'),
        'is_exists_tax_values': report_intermediate_data.get('is_exists_tax_values'),
        'brands_share_in_revenue_dict': json.dumps(brands_share_in_revenue_dict, ensure_ascii=False),
        'stocks_share_in_revenue_dict': json.dumps(stocks_share_in_revenue_dict, ensure_ascii=False)
    }




