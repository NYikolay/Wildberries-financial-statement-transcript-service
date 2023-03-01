import json
import itertools
from typing import List

from django.db.models import (
    Sum, Q, FloatField,
    F, IntegerField, Subquery,
    OuterRef, Value,
    Case, When, Func,
    CharField, Min, Max, Count)
from django.db.models.functions import Coalesce, TruncYear, ExtractYear, ExtractWeek

from users.models import (
    SaleObject, User, ClientUniqueProduct,
    NetCost, SaleReport, TaxRate)


def get_aggregate_sum_dicts() -> dict:
    """
    Returns Coalesce(Sum()) objects for each of the queries with more objects in the aggregation.
    """
    argument_names = [
        'sales_sum',
        'returns_sum',
        'storno_sales_sum',
        'correct_sales_sum',
        'storno_returns_sum',
        'correct_returns_sum',
        'сommission_sales_sum',
        'сommission_storno_sales_sum',
        'сommission_correct_sales_sum',
        'сommission_returns_sum',
        'сommission_storno_returns_sum',
        'сommission_correct_returns_sum',
        'sales_quantity_sum',
        'strono_sales_quantity_sum',
        'correct_sales_quantity_sum',
        'returns_quantity_sum',
        'strono_returns_quantity_sum',
        'correct_return_quantity_sum'
    ]
    filter_names = [
        'Продажа',
        'Возврат',
        'Сторно продаж',
        'Корректная продажа',
        'Сторно возвратов',
        'Корректный возврат',
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат',
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат'
    ]
    aggregate_fields_names = [
        *['retail_price_withdisc_rub'] * 6,
        *['ppvz_for_pay'] * 6,
        *['quantity'] * 6
    ]
    net_costs_argument_names = [
        'netcost_sale_sum',
        'netcost_storno_sale_sum',
        'netcost_correct_sale_sum',
        'netcost_return_sum',
        'net_cost_strono_returns_sum',
        'net_cost_correct_return_sum'
    ]
    net_costs_filter_names = [
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат'
    ]
    tax_rates_argument_names = [
        'tax_sale_sum',
        'tax_storno_sale_sum',
        'tax_correct_sale_sum',
        'tax_return_sum',
        'tax_storno_return_sum',
        'tax_correct_return_sum'
    ]
    tax_rates_filter_names = [
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат'
    ]

    sum_aggregation_objs_dict = {}

    for arg_name, field_name, filter_name in zip(argument_names, aggregate_fields_names, filter_names):
        sum_aggregation_objs_dict[arg_name] = Coalesce(
            Sum(field_name, filter=Q(supplier_oper_name=filter_name)), 0, output_field=FloatField()
        )

    net_costs_sum_aggregation_objs = {}

    for arg_name, filter_name in zip(net_costs_argument_names, net_costs_filter_names):
        net_costs_sum_aggregation_objs[arg_name] = Coalesce(
            Sum('net_cost', filter=Q(supplier_oper_name=filter_name)), 0, output_field=FloatField()
        )

    tax_rates_sum_aggregation_objs = {}

    for arg_name, filter_name in zip(tax_rates_argument_names, tax_rates_filter_names):
        tax_rates_sum_aggregation_objs[arg_name] = Coalesce(
            Sum('price_including_tax', filter=Q(supplier_oper_name=filter_name)), 0, output_field=FloatField()
        )

    return {
        'sum_aggregation_objs_dict': sum_aggregation_objs_dict,
        'net_costs_sum_aggregation_objs': net_costs_sum_aggregation_objs,
        'tax_rates_sum_aggregation_objs': tax_rates_sum_aggregation_objs
    }


def get_calculated_financials_by_weeks(
        sales_objects_figures: dict,
        supplier_costs_values: dict,
        sale_report_wb_costs_sum: dict,
) -> dict:
    """
    Based on the results of sales aggregations, it calculates and returns user-ready figures.
    CALCULATIONS ARE NOT ROUNDED, ROUNDING ONLY WHEN RETURNING TO THE USER
    """

    revenue: float = \
        sales_objects_figures.get('sales_sum') - \
        sales_objects_figures.get('returns_sum') - \
        sales_objects_figures.get('storno_sales_sum') + \
        sales_objects_figures.get('correct_sales_sum') - \
        sales_objects_figures.get('storno_returns_sum') + \
        sales_objects_figures.get('correct_returns_sum')

    sales_quantity_value: float = \
        sales_objects_figures.get('sales_quantity_sum') - \
        sales_objects_figures.get('strono_sales_quantity_sum') + \
        sales_objects_figures.get('correct_sales_quantity_sum')

    returns_quantity_value: float = \
        sales_objects_figures.get('returns_quantity_sum') - \
        sales_objects_figures.get('strono_returns_quantity_sum') + \
        sales_objects_figures.get('correct_return_quantity_sum')

    commission: float = \
        (sales_objects_figures.get('sales_sum') - sales_objects_figures.get('сommission_sales_sum')) - \
        (sales_objects_figures.get('returns_sum') - sales_objects_figures.get('сommission_returns_sum')) - \
        (sales_objects_figures.get('storno_sales_sum') - sales_objects_figures.get('сommission_storno_sales_sum')) + \
        (sales_objects_figures.get('storno_returns_sum') - sales_objects_figures.get('сommission_storno_returns_sum')) + \
        (sales_objects_figures.get('correct_sales_sum') - sales_objects_figures.get('сommission_correct_sales_sum')) - \
        (sales_objects_figures.get('correct_returns_sum') - sales_objects_figures.get('сommission_correct_returns_sum'))

    logistics: float = sales_objects_figures.get('logistic_sum')
    supplier_costs_sum: float = supplier_costs_values.get('supplier_costs_sum')

    tax_value: float = \
        sales_objects_figures.get('tax_sale_sum') - \
        sales_objects_figures.get('tax_storno_sale_sum') + \
        sales_objects_figures.get('tax_correct_sale_sum') - \
        sales_objects_figures.get('tax_return_sum') - \
        sales_objects_figures.get('tax_storno_return_sum') + \
        sales_objects_figures.get('tax_correct_return_sum')

    net_costs_sum: float = \
        (sales_objects_figures.get('netcost_sale_sum') -
         sales_objects_figures.get('netcost_storno_sale_sum') +
         sales_objects_figures.get('netcost_correct_sale_sum')) - \
        (sales_objects_figures.get('netcost_return_sum') -
         sales_objects_figures.get('net_cost_strono_returns_sum') +
         sales_objects_figures.get('net_cost_correct_return_sum'))

    if net_costs_sum > 0:
        marginality: float = ((revenue - net_costs_sum) / revenue) * 100 if revenue > 0 else 0
    else:
        marginality = 0

    profit: float = \
        revenue - net_costs_sum - commission - logistics - \
        sales_objects_figures.get('penalty_sum') - sales_objects_figures.get('additional_payment_sum') - \
        sale_report_wb_costs_sum.get('total_wb_costs_sum') - tax_value - supplier_costs_sum

    profitability: float = (profit / revenue) * 100 if revenue > 0 else 0

    return {
        'date_from': sales_objects_figures.get('date_from').strftime("%d.%m.%Y"),
        'date_to': sales_objects_figures.get('date_to').strftime("%d.%m.%Y"),
        'week_num': sales_objects_figures.get('week_num'),
        'revenue': revenue,
        'sales_amount': sales_quantity_value,
        'returns_amount': returns_quantity_value,
        'logistics': logistics,
        'net_costs_sum': net_costs_sum,
        'marginality': marginality,
        'commission': commission,
        'supplier_costs': supplier_costs_sum,
        'wb_costs': sale_report_wb_costs_sum.get('total_wb_costs_sum'),
        'tax': tax_value,
        'profit': profit,
        'profitability': profitability,
        'penalty': sales_objects_figures.get('penalty_sum'),
        'additional_payment_sum': sales_objects_figures.get('additional_payment_sum')
    }


def get_total_financials(report_intermediate_data, supplier_costs_sum_list, wb_costs_sum_list) -> dict:
    revenue_total = []
    sales_amount_total = []
    returns_amount_total = []
    logistics_total = []
    net_costs_sum_total = []
    marginality_total = []
    commission_total = []
    supplier_costs_total = []
    wb_costs_total = []
    tax_total = []
    profit_total = []
    profitability_total = []
    reports_by_week = []
    penalty_total = []
    additional_payment_sum_total = []

    for inter_data, supplier_cost, wb_cost in zip(report_intermediate_data, supplier_costs_sum_list, wb_costs_sum_list):
        data: dict = get_calculated_financials_by_weeks(inter_data, supplier_cost, wb_cost)
        reports_by_week.append(data)
        revenue_total.append(data.get('revenue'))
        sales_amount_total.append(data.get('sales_amount'))
        returns_amount_total.append(data.get('returns_amount'))
        logistics_total.append(data.get('logistics'))
        net_costs_sum_total.append(data.get('net_costs_sum'))
        commission_total.append(data.get('commission'))
        supplier_costs_total.append(data.get('supplier_costs'))
        wb_costs_total.append(data.get('wb_costs'))
        marginality_total.append(data.get('marginality'))
        tax_total.append(data.get('tax'))
        profit_total.append(data.get('profit'))
        profitability_total.append(data.get('profitability'))
        penalty_total.append(data.get('penalty'))
        additional_payment_sum_total.append(data.get('additional_payment_sum'))

    if sum(net_costs_sum_total) > 0:
        marginality = ((sum(revenue_total) - sum(net_costs_sum_total)) / sum(revenue_total) * 100) \
            if sum(revenue_total) > 0 else 0
    else:
        marginality = 0

    profitability_total = round((sum(profit_total) / sum(revenue_total) * 100)) if sum(revenue_total) > 0 else 0

    return {
        'revenue_total': sum(revenue_total),
        'sales_amount_total': sum(sales_amount_total),
        'returns_amount_total': sum(returns_amount_total),
        'logistics_total': round(sum(logistics_total)),
        'net_costs_sum_total': round(sum(net_costs_sum_total)),
        'marginality_total': round(marginality),
        'commission_total': round(sum(commission_total)),
        'supplier_costs_total': round(sum(supplier_costs_total)),
        'wb_costs_total': round(sum(wb_costs_total)),
        'tax_total': round(sum(tax_total)),
        'profit_total': round(sum(profit_total)),
        'profitability_total': profitability_total,
        'reports_by_week': json.dumps(reports_by_week, ensure_ascii=False),
        'penalty_total': round(sum(penalty_total)),
        'additional_payment_sum_total': round(sum(additional_payment_sum_total))
    }


def get_calculated_financials_by_weeks_by_products(sales_objects_by_product_figures, revenue_total: float) -> dict:

    sales_quantity_value: float = \
        sales_objects_by_product_figures.get('sales_quantity_sum') - \
        sales_objects_by_product_figures.get('strono_sales_quantity_sum') + \
        sales_objects_by_product_figures.get('correct_sales_quantity_sum')

    returns_quantity_value: float = \
        sales_objects_by_product_figures.get('returns_quantity_sum') - \
        sales_objects_by_product_figures.get('strono_returns_quantity_sum') + \
        sales_objects_by_product_figures.get('correct_return_quantity_sum')

    revenue_by_article: float = \
        sales_objects_by_product_figures.get('sales_sum') - \
        sales_objects_by_product_figures.get('returns_sum') - \
        sales_objects_by_product_figures.get('storno_sales_sum') + \
        sales_objects_by_product_figures.get('correct_sales_sum') - \
        sales_objects_by_product_figures.get('storno_returns_sum') + \
        sales_objects_by_product_figures.get('correct_returns_sum')

    share_in_profits: float = (revenue_by_article / revenue_total) * 100 if revenue_total > 0 else 0

    net_costs_sum: float = \
        (sales_objects_by_product_figures.get('netcost_sale_sum') -
         sales_objects_by_product_figures.get('netcost_storno_sale_sum') +
         sales_objects_by_product_figures.get('netcost_correct_sale_sum')) - \
        (sales_objects_by_product_figures.get('netcost_return_sum') -
         sales_objects_by_product_figures.get('net_cost_strono_returns_sum') +
         sales_objects_by_product_figures.get('net_cost_correct_return_sum'))

    if net_costs_sum > 0:
        product_marginality: float = ((revenue_by_article - net_costs_sum) / revenue_by_article) * 100 \
            if revenue_by_article > 0 else 0
    else:
        product_marginality: float = 0

    product_total = {
        'nm_id': sales_objects_by_product_figures.get('nm_id'),
        'sales_quantity_value': round(sales_quantity_value),
        'returns_quantity_value': round(returns_quantity_value),
        'revenue_by_article': round(revenue_by_article),
        'share_in_profits': round(share_in_profits, 2),
        'product_marginality': round(product_marginality),
    }

    return product_total


def handle_revenues_list_by_filter(revenues_list: list, revenue_total: float) -> dict:
    all_revenues: List[tuple] = []

    for filter_dict in revenues_list:
        for key, value in filter_dict.items():
            all_revenues.append((key, value / revenue_total * 100))

    sorted_all_revenues: List[tuple] = list(sorted(all_revenues, key=lambda x: x[1], reverse=True))

    revenues: dict = dict(sorted_all_revenues[:7])

    if other_share_in_revenues := sorted_all_revenues[7:]:
        revenues['остальные'] = sum(map(lambda el: el[1], other_share_in_revenues))

    return revenues


def get_revenues_list_by_filter(request, current_api_key, period_filter_data, filter_name: str) -> list:
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()
    sum_aggregation_objs_dict: dict = general_dict_aggregation_objs.get('sum_aggregation_objs_dict', None)

    sales_objs_by_stock = SaleObject.objects.filter(
        period_filter_data,
        owner=request.user,
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
    )

    stock_revenues_list: List[dict] = []

    for stock_sale in sales_objs_by_stock:
        stock_revenues_list.append({
            stock_sale.get(filter_name): stock_sale.get('total_filter_revenue'),
        })

    return stock_revenues_list


def generate_period_filter_conditions(period_filter_data: list):
    empty_q_obj = Q()

    for filter_data in period_filter_data:
        empty_q_obj |= Q(year=filter_data.get('year'), week_num__in=filter_data.get('week_nums'))

    return empty_q_obj


def get_report(request, current_api_key, period_filter_data: list) -> dict:
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()
    sum_aggregation_objs_dict: dict = general_dict_aggregation_objs.get('sum_aggregation_objs_dict', None)
    net_costs_sum_aggregations_objs: dict = general_dict_aggregation_objs.get('net_costs_sum_aggregation_objs', None)
    tax_rates_sum_aggregation_objs: dict = general_dict_aggregation_objs.get('tax_rates_sum_aggregation_objs', None)
    filter_data = generate_period_filter_conditions(period_filter_data)

    tax_rates_objects = TaxRate.objects.filter(
        api_key=current_api_key
    ).order_by('-commencement_date').only('tax_rate', 'commencement_date')

    tax_rates_case_dict: list = [
        When(
            sale_dt__gte=obj.commencement_date, then=Value(obj.tax_rate)
        ) for obj in tax_rates_objects
    ]

    report_intermediate_data = SaleObject.objects.filter(
        filter_data,
        owner=request.user,
        api_key=current_api_key,
    ).annotate(
        price_including_tax=(
                (F('retail_price_withdisc_rub') *
                 Case(*tax_rates_case_dict, default=Value(0), output_field=FloatField())) / 100
        ),
        net_cost=Coalesce(
            Subquery(
                NetCost.objects.filter(
                    product_id=Subquery(
                        ClientUniqueProduct.objects.filter(nm_id=OuterRef(OuterRef('nm_id'))).values('pk')[:1]
                    ),
                    cost_date__lte=OuterRef('order_dt'),
                ).order_by('-cost_date').values('amount')[:1]
            ),
            Value(0),
            output_field=FloatField(),
        ),
    ).order_by('date_from').values('year', 'week_num').annotate(
        **sum_aggregation_objs_dict,
        **tax_rates_sum_aggregation_objs,
        **net_costs_sum_aggregations_objs,
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
        logistic_sum=(
                Coalesce(Sum(
                    'delivery_rub',
                    filter=~Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField()) -
                Coalesce(Sum(
                    'delivery_rub',
                    filter=Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField())
        ),
        penalty_sum=Coalesce(Sum('penalty'), 0, output_field=FloatField()),
        additional_payment_sum=Coalesce(Sum('additional_payment'), 0, output_field=FloatField())
    )

    supplier_costs_sum_list = SaleReport.objects.filter(
        id__in=Subquery(
            SaleReport.objects.filter(
                filter_data,
                owner=request.user,
                api_key=current_api_key,
            ).distinct('create_dt').values_list('id', flat=True)
        )).order_by('date_from').values('year', 'week_num').annotate(
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
        supplier_costs_sum=Coalesce(Sum('supplier_costs'), 0, output_field=FloatField())
    )

    wb_costs_sum_list = SaleReport.objects.filter(
        filter_data,
        owner=request.user,
        api_key=current_api_key,
    ).order_by('date_from').values('year', 'week_num').annotate(
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
        total_wb_costs_sum=
        Sum(
            Coalesce(F('storage_cost'), 0, output_field=FloatField()) +
            Coalesce(F('cost_paid_acceptance'), 0, output_field=FloatField()) +
            Coalesce(F('other_deductions'), 0, output_field=FloatField())
        )
    )

    sale_objects_by_products = SaleObject.objects.filter(
        filter_data,
        owner=request.user,
        api_key=current_api_key,
        nm_id__isnull=False
    ).annotate(
        net_cost=Coalesce(
            Subquery(
                NetCost.objects.filter(
                    product_id=Subquery(
                        ClientUniqueProduct.objects.filter(nm_id=OuterRef(OuterRef('nm_id'))).values('pk')[:1]
                    ),
                    cost_date__lte=OuterRef('order_dt'),
                ).order_by('-cost_date').values('amount')[:1]
            ),
            Value(0),
            output_field=FloatField(),
        )
    ).order_by('brand_name', 'nm_id').values('nm_id').annotate(
        **sum_aggregation_objs_dict,
        **net_costs_sum_aggregations_objs,
        logistic_sum=(
                Coalesce(Sum(
                    'delivery_rub',
                    filter=~Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField()) -
                Coalesce(Sum(
                    'delivery_rub',
                    filter=Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField())
        ),
        penalty_sum=Coalesce(Sum('penalty'), 0, output_field=FloatField()),
        additional_payment_sum=Coalesce(Sum('additional_payment'), 0, output_field=FloatField())
    )

    unique_articles = ClientUniqueProduct.objects.filter(
        api_key=current_api_key,
    ).values_list('nm_id', 'image')

    is_empty_reports_values = SaleReport.objects.filter(
        filter_data,
        Q(storage_cost__isnull=True) |
        Q(cost_paid_acceptance__isnull=True) |
        Q(other_deductions__isnull=True) |
        Q(supplier_costs__isnull=True),
        owner=request.user,
        api_key=current_api_key,
        ).exists()

    is_empty_netcosts_values = ClientUniqueProduct.objects.filter(
        api_key=current_api_key,
        cost_prices__isnull=True
    ).exists()

    is_empty_tax_values = TaxRate.objects.filter(
        api_key=current_api_key
    ).exists()

    totals: dict = get_total_financials(report_intermediate_data, supplier_costs_sum_list, wb_costs_sum_list)

    articles_images_dict: dict = {}

    for nm_id, img in unique_articles:
        articles_images_dict[nm_id] = img

    products_financials: list = []

    for sale in sale_objects_by_products:
        product_fin: dict = get_calculated_financials_by_weeks_by_products(sale, totals.get('revenue_total'))
        product_fin['image'] = articles_images_dict.get(product_fin.get('nm_id'))
        products_financials.append(product_fin)

    brand_revenues_list: list = get_revenues_list_by_filter(request, current_api_key, filter_data, 'brand_name')
    stock_revenues_list: list = get_revenues_list_by_filter(request, current_api_key, filter_data, 'office_name')
    brands_share_in_revenue_dict: dict = handle_revenues_list_by_filter(brand_revenues_list, totals.get('revenue_total'))
    stocks_share_in_revenue_dict: dict = handle_revenues_list_by_filter(stock_revenues_list, totals.get('revenue_total'))

    return {
        **totals,
        'report_by_products': products_financials,
        'is_empty_reports_values': is_empty_reports_values,
        'is_empty_netcosts_values': is_empty_netcosts_values,
        'is_empty_tax_values': is_empty_tax_values,
        'brands_share_in_revenue_dict': json.dumps(brands_share_in_revenue_dict, ensure_ascii=False),
        'stocks_share_in_revenue_dict': json.dumps(stocks_share_in_revenue_dict, ensure_ascii=False)
    }



