from collections import defaultdict
from typing import List
import datetime
from itertools import groupby
import statistics
from django.db.models import (
    Sum, Q, FloatField,
    F, Subquery,
    OuterRef, Value,
    Case, When, Min, Max, Count, Func, IntegerField, Window, ExpressionWrapper, StdDev, Avg)
from django.db.models.functions import Coalesce, Round

from reports.services.report_generation_services.generate_priod_filters_services import \
    generate_period_filter_conditions
from users.models import (SaleObject, ClientUniqueProduct, NetCost, SaleReport, TaxRate)

from reports.services.report_generation_services.generating_sum_aggregation_objs_service import get_aggregate_sum_dicts


def get_financials_annotation_objects():
    revenue_by_article = ExpressionWrapper(
        F('retail_sales_sum') - F('retail_storno_sales_sum') + F('retail_correct_sales_sum') - F(
            'retail_return_sum') + F('retail_storno_returns_sum') - F('retail_correct_returns_sum') + F(
            'retail_marriage_payment_sum') + F('retail_payment_lost_marriage_sum') + F(
            'retail_partial_compensation_marriage_sum') + F('retail_advance_payment_goods_without_payment_sum'),
        output_field=FloatField()
    )

    share_in_revenue = Case(
        When(total_revenue__gt=0, then=((F('revenue_by_article') / F('total_revenue')) * 100)),
        default=Value(0.0),
        output_field=FloatField()
    )

    net_costs_sum = ExpressionWrapper(
        F('netcost_sale_sum') - F('netcost_storno_sale_sum') + F('netcost_correct_sale_sum') - F(
            'netcost_return_sum') + F('net_cost_strono_returns_sum') - F('net_cost_correct_return_sum') + F(
            'net_cost_marriage_payment_sum') + F('net_cost_payment_lost_marriage_sum') + F(
            'net_cost_partial_compensation_marriage_sum') + F('net_cost_advance_payment_goods_without_payment_sum'),
        output_field=FloatField()
    )

    product_marginality = Case(
        When(net_costs_sum__gt=0, then=(F('revenue_by_article') / F('net_costs_sum')) * 100),
        default=Value(0.0),
        output_field=FloatField()
    )

    share_in_number = ExpressionWrapper((1 / F('total_products_count')) * 100, output_field=FloatField())

    return {
        "revenue_by_article": revenue_by_article,
        "share_in_revenue": share_in_revenue,
        "net_costs_sum": net_costs_sum,
        "product_marginality": product_marginality,
        "share_in_number": share_in_number
    }


def get_past_months_filters():
    last_year = datetime.date.today() - datetime.timedelta(days=365)
    weeks_by_years = defaultdict(set)

    for i in range(52):
        current_date = last_year + datetime.timedelta(weeks=i)
        year, week_num, _ = current_date.isocalendar()
        weeks_by_years[year].add(week_num)

    new_filter_list = [
        {
            'year': int(year),
            'week_nums': sorted(weeks_by_years[year])
        } for year in weeks_by_years
    ]

    filters = generate_period_filter_conditions(new_filter_list)

    return {
        'filters': filters,
        'weeks_by_years': weeks_by_years
    }


def get_calculated_financials_by_products(
        current_user,
        current_api_key,
        filter_period_conditions,
        sum_aggregation_objs_dict,
        net_costs_sum_aggregations_objs,
        total_revenue,
        total_products_count,
        annotations_objs
):

    calculated_financials = SaleObject.objects.filter(
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
        nm_id__isnull=False
    ).annotate(
        net_cost=Subquery(
            NetCost.objects.filter(
                product=OuterRef('product'),
                cost_date__lte=OuterRef('order_dt')
            ).order_by('-cost_date').values('amount')[:1]
        ),
    ).order_by('brand_name', 'nm_id').values('nm_id').annotate(
        **sum_aggregation_objs_dict,
        **net_costs_sum_aggregations_objs,
        image=F('product__image'),
        logistic_sum=(
                Coalesce(Sum(
                    'delivery_rub',
                    filter=~Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField()) -
                Coalesce(Sum(
                    'delivery_rub',
                    filter=Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField())
        ),
        penalty_sum=Coalesce(Sum('penalty'), 0, output_field=FloatField()),
        additional_payment_sum=Coalesce(Sum('additional_payment'), 0, output_field=FloatField()),
    ).annotate(
        total_revenue=Value(total_revenue, output_field=FloatField()),
        total_products_count=Value(total_products_count, output_field=FloatField()),
        **annotations_objs,
    ).values('nm_id', 'image', 'revenue_by_article', 'share_in_revenue', 'product_marginality', 'share_in_number')

    return calculated_financials


def get_nm_ids_revenues_by_weeks(current_nm_ids_set, sum_aggregation_objs_dict, filters):

    revenues_queryset = SaleObject.objects.filter(
        filters,
        nm_id__in=current_nm_ids_set
    ).order_by('week_num').values('week_num', 'year').annotate(
        **sum_aggregation_objs_dict,
        revenue_by_article=ExpressionWrapper(
            F('retail_sales_sum') - F('retail_storno_sales_sum') + F('retail_correct_sales_sum') - F(
                'retail_return_sum') + F('retail_storno_returns_sum') - F('retail_correct_returns_sum') + F(
                'retail_marriage_payment_sum') + F('retail_payment_lost_marriage_sum') + F(
                'retail_partial_compensation_marriage_sum') + F('retail_advance_payment_goods_without_payment_sum'),
            output_field=FloatField()),
    ).order_by('-nm_id').values('week_num', 'nm_id', 'revenue_by_article', 'year')

    return revenues_queryset


def generate_abc_report_values(calculated_financials_by_products):

    sorted_calculated_values_by_products = sorted(
        calculated_financials_by_products, key=lambda x: x['share_in_revenue'], reverse=True)

    current_nm_ids = set()

    last_share_increasing_proportion = 0

    for sale in sorted_calculated_values_by_products:
        increasing_proportion = sale.get('share_in_revenue') + last_share_increasing_proportion

        sale['increasing_proportion'] = increasing_proportion
        sale['group_abc'] = 'A' if increasing_proportion <= 80 else 'B' if 80 < increasing_proportion <= 95 else 'C'

        last_share_increasing_proportion = increasing_proportion

        current_nm_ids.add(sale.get('nm_id'))

    total_abc_dict = {group: {"revenue": 0, "share": 0} for group in ["A", "B", "C"]}

    for value in sorted_calculated_values_by_products:
        total_abc_dict.get(value.get("group_abc"))["revenue"] += value.get("revenue_by_article")
        total_abc_dict.get(value.get("group_abc"))["share"] += value.get("share_in_number")

    return {
        "total_abc_dict": total_abc_dict,
        "current_nm_ids": current_nm_ids,
        "abc_values_by_nm_ids": sorted_calculated_values_by_products
    }


def remove_zeros(lst):
    first_positive_index = next((i for i, x in enumerate(lst) if x > 0), None)
    last_positive_index = next((i for i, x in enumerate(reversed(lst)) if x > 0), None)

    if first_positive_index is None:
        return []

    if last_positive_index is None:
        return lst[first_positive_index:]

    last_positive_index = len(lst) - last_positive_index - 1

    return lst[first_positive_index:last_positive_index + 1]


def generate_xyz_report_values(sum_aggregation_objs_dict, current_nm_ids_set):
    past_months_values = get_past_months_filters()
    weeks_by_years = past_months_values.get('weeks_by_years')

    revenues_by_weeks_queryset = get_nm_ids_revenues_by_weeks(
        current_nm_ids_set, sum_aggregation_objs_dict, past_months_values.get('filters')
    )

    nm_id_weeks_dict = {
        nm_id: {week_num: list(values) for week_num, values in weeks_by_years.items()} for nm_id in current_nm_ids_set
    }

    revenues_by_weeks_dict = {nm_id: {} for nm_id in current_nm_ids_set}
    for value in revenues_by_weeks_queryset:
        revenues_by_weeks_dict[value['nm_id']][value['week_num']] = value['revenue_by_article']

    nm_id_weeks_list = {key: sum((value for value in nm_id_weeks_dict[key].values()), []) for key in nm_id_weeks_dict}

    final_revenues_by_nm_ids: dict = {
        k: [revenues_by_weeks_dict[k].get(i, 0.0) for i in nm_id_weeks_list[k]] for k in nm_id_weeks_list
    }

    total_xyz_dict = {}

    for nm_id, revenues_by_week_lst in final_revenues_by_nm_ids.items():
        new_revenues_by_week_lst = remove_zeros(revenues_by_week_lst)

        if len(new_revenues_by_week_lst) <= 1:
            continue

        stdev_value = statistics.stdev(new_revenues_by_week_lst)
        avg_sum = sum(new_revenues_by_week_lst) / len(new_revenues_by_week_lst)
        coefficient_xyz = (stdev_value / avg_sum) * 100
        total_xyz_dict[nm_id] = {
            'coefficient_xyz': coefficient_xyz,
            'group': 'X' if coefficient_xyz <= 10 else 'Y' if 25 >= coefficient_xyz > 10 else 'Z'
        }

    return total_xyz_dict


def make_abc_xyz_data_set(abc_values_by_nm_ids, xyz_report):

    abc_xyz_data_set = []
    for abc_dict in abc_values_by_nm_ids:
        if xyz_report.get(abc_dict.get('nm_id')):
            temp_dict = dict()

            temp_dict['nm_id'] = abc_dict.get('nm_id')
            temp_dict['general_group'] = (
                    abc_dict.get('group_abc') + xyz_report.get(abc_dict.get('nm_id')).get('group')
            )
            temp_dict['revenue'] = abc_dict.get('revenue_by_article')
            abc_xyz_data_set.append(temp_dict)
        else:
            continue

    sums = {}
    for d in abc_xyz_data_set:
        if d['general_group'] not in sums:
            sums[d['general_group']] = 0
        sums[d['general_group']] += d['revenue']

    result = [{'general_group': k, 'revenue': v} for k, v in sums.items()]

    return result


def get_abc_xyz_report(
        current_user,
        current_api_key,
        filter_period_conditions,
        sum_aggregation_objs_dict,
        net_costs_sum_aggregations_objs,
        total_revenue,
        total_products_count
):
    annotations_objs = get_financials_annotation_objects()

    calculated_financials_bu_products = list(get_calculated_financials_by_products(
        current_user, current_api_key, filter_period_conditions,
        sum_aggregation_objs_dict, net_costs_sum_aggregations_objs,
        total_revenue, total_products_count, annotations_objs
    ))

    abc_report = generate_abc_report_values(calculated_financials_bu_products)
    xyz_report = generate_xyz_report_values(sum_aggregation_objs_dict, abc_report.get('current_nm_ids'))

    abc_xyz_report = make_abc_xyz_data_set(abc_report.get('abc_values_by_nm_ids'), xyz_report)

    return {
        "products_values_by_nm_id": abc_report.get('abc_values_by_nm_ids'),
        "abc_xyz_report": abc_xyz_report,
        "abc_report": abc_report.get('total_abc_dict')
    }
