from reports.services.report_generation_services.formula_calculation_service import calculate_share_in_revenue
from reports.services.report_generation_services.generating_sum_aggregation_objs_service import get_aggregate_sum_dicts
from users.models import SaleObject
from django.db.models import F, Q
from typing import List


def get_revenue_by_filter(
        current_user,
        current_api_key,
        period_filter_data,
        filter_name: str
) -> List[dict]:
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()
    sum_aggregation_objs_dict: dict = general_dict_aggregation_objs.get('sum_aggregation_objs_dict')

    revenue_by_filter_list = SaleObject.objects.filter(
        ~Q(supplier_oper_name='Логистика') & ~Q(supplier_oper_name='Логистика сторно'),
        period_filter_data.get('period_q_obj'),
        owner=current_user,
        api_key=current_api_key,
        brand_name__isnull=False
    ).values(filter_name).annotate(
        sales_sum=sum_aggregation_objs_dict.get('sales_sum'),
        returns_sum=sum_aggregation_objs_dict.get('returns_sum'),
        storno_sales_sum=sum_aggregation_objs_dict.get('storno_sales_sum'),
        correct_sales_sum=sum_aggregation_objs_dict.get('correct_sales_sum'),
        storno_returns_sum=sum_aggregation_objs_dict.get('storno_returns_sum'),
        correct_returns_sum=sum_aggregation_objs_dict.get('correct_returns_sum')
    ).annotate(
        total_filter_revenue=
        F('sales_sum') - F('returns_sum') + F('storno_sales_sum') -
        F('correct_sales_sum') - F('storno_returns_sum') + F('correct_returns_sum')
    ).values(filter_name, 'total_filter_revenue')

    return revenue_by_filter_list


def get_share_in_revenue(
        current_user,
        current_api_key,
        period_filter_data,
        revenue_total: float,
        filter_name: str,
):
    revenues_list = get_revenue_by_filter(current_user, current_api_key, period_filter_data, filter_name)

    all_revenues: List[tuple] = [
        (
            filter_dict.get(filter_name),
            calculate_share_in_revenue(filter_dict.get('total_filter_revenue'), revenue_total)
        ) for filter_dict in revenues_list
    ]

    sorted_all_revenues: List[tuple] = list(sorted(all_revenues, key=lambda x: x[1], reverse=True))

    shares_in_revenues: dict = dict(sorted_all_revenues[:7])

    if other_share_in_revenues := sorted_all_revenues[7:]:
        shares_in_revenues['остальные'] = sum(map(lambda el: el[1], other_share_in_revenues))

    return shares_in_revenues
