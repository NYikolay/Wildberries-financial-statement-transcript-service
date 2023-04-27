from reports.services.report_generation_services.formula_calculation_service import calculate_share_in_revenue
from reports.services.report_generation_services.generating_sum_aggregation_objs_service import get_aggregate_sum_dicts
from users.models import SaleObject
from typing import List
from django.db.models import (
    Sum, Q, FloatField,
    F, Value,
    Case, When, ExpressionWrapper)
from django.db.models.functions import Coalesce


def get_revenue_by_filter(
        current_user,
        current_api_key,
        filter_period_conditions,
        filter_name: str
) -> List[dict]:
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()
    sum_aggregation_objs_dict: dict = general_dict_aggregation_objs.get('sum_aggregation_objs_dict')

    revenue_by_filter_list = SaleObject.objects.filter(
        ~Q(nm_id=99866376),
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
        brand_name__isnull=False,
        nm_id__isnull=False
    ).values(filter_name).annotate(
        retail_sales_sum=sum_aggregation_objs_dict.get('retail_sales_sum'),
        retail_return_sum=sum_aggregation_objs_dict.get('retail_return_sum'),
        retail_storno_sales_sum=sum_aggregation_objs_dict.get('retail_storno_sales_sum'),
        retail_correct_sales_sum=sum_aggregation_objs_dict.get('retail_correct_sales_sum'),
        retail_storno_returns_sum=sum_aggregation_objs_dict.get('retail_storno_returns_sum'),
        retail_correct_returns_sum=sum_aggregation_objs_dict.get('retail_correct_returns_sum'),
        retail_marriage_payment_sum=sum_aggregation_objs_dict.get('retail_marriage_payment_sum'),
        retail_sales_payment_lost_marriage_sum=sum_aggregation_objs_dict.get(
            'retail_sales_payment_lost_marriage_sum'),
        retail_returns_payment_lost_marriage_sum=sum_aggregation_objs_dict.get(
            'retail_returns_payment_lost_marriage_sum'),
        retail_partial_compensation_marriage_sum=sum_aggregation_objs_dict.get(
            'retail_partial_compensation_marriage_sum'),
        retail_sales_advance_payment_goods_without_payment_sum=sum_aggregation_objs_dict.get(
            'retail_sales_advance_payment_goods_without_payment_sum'),
        retail_returns_advance_payment_goods_without_payment_sum=sum_aggregation_objs_dict.get(
            'retail_returns_advance_payment_goods_without_payment_sum')
    ).annotate(
        total_filter_revenue=Coalesce(
            ExpressionWrapper(
                F('retail_sales_sum') - F('retail_storno_sales_sum') + F('retail_correct_sales_sum') -
                F('retail_return_sum') + F('retail_storno_returns_sum') - F('retail_correct_returns_sum') +
                F('retail_marriage_payment_sum') + F('retail_sales_payment_lost_marriage_sum') -
                F('retail_returns_payment_lost_marriage_sum') +
                F('retail_partial_compensation_marriage_sum') +
                F('retail_sales_advance_payment_goods_without_payment_sum') -
                F('retail_returns_advance_payment_goods_without_payment_sum'),
                output_field=FloatField()
            ), Value(0.0), output_field=FloatField())
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
