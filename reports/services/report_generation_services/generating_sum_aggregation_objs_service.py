
from django.db.models import (
    Sum, Q, FloatField,
    F, Value,
    Case, When, ExpressionWrapper)
from django.db.models.functions import Coalesce


def get_financials_annotation_objects() -> dict:
    revenue_by_article = Coalesce(
        ExpressionWrapper(
            F('retail_sales_sum') - F('retail_storno_sales_sum') + F('retail_correct_sales_sum') - F(
                'retail_return_sum') + F('retail_storno_returns_sum') - F('retail_correct_returns_sum') + F(
                'retail_marriage_payment_sum') + F('retail_payment_lost_marriage_sum') + F(
                'retail_partial_compensation_marriage_sum') - F('retail_advance_payment_goods_without_payment_sum'),
            output_field=FloatField()
        ), Value(0.0), output_field=FloatField())

    share_in_revenue = Coalesce(Case(
        When(total_revenue__gt=0, then=((F('revenue_by_article') / F('total_revenue')) * 100)),
        default=Value(0.0),
        output_field=FloatField()
    ), Value(0.0), output_field=FloatField())

    net_costs_sum = Coalesce(
        ExpressionWrapper(
            F('netcost_sale_sum') - F('netcost_storno_sale_sum') + F('netcost_correct_sale_sum') - F(
                'netcost_return_sum') + F('net_cost_strono_returns_sum') - F('net_cost_correct_return_sum') + F(
                'net_cost_marriage_payment_sum') + F('net_cost_payment_lost_marriage_sum') + F(
                'net_cost_partial_compensation_marriage_sum') - F('net_cost_advance_payment_goods_without_payment_sum'),
            output_field=FloatField()
        ), Value(0.0), output_field=FloatField())

    product_marginality = Coalesce(Case(
        When(net_costs_sum__gt=0, then=(F('revenue_by_article') / F('net_costs_sum')) * 100),
        default=Value(0.0),
        output_field=FloatField()
    ), Value(0.0), output_field=FloatField())

    share_in_number = Coalesce(Case(
        When(total_products_count__gt=0, then=((1 / F('total_products_count')) * 100)),
        default=Value(0.0),
        output_field=FloatField()
    ), Value(0.0), output_field=FloatField())

    return {
        "revenue_by_article": revenue_by_article,
        "share_in_revenue": share_in_revenue,
        "net_costs_sum": net_costs_sum,
        "product_marginality": product_marginality,
        "share_in_number": share_in_number
    }


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
        'marriage_payment_sum',
        'payment_lost_marriage_sum',
        'partial_compensation_marriage_sum',
        'advance_payment_goods_without_payment_sum',
        'сommission_sales_sum',
        'сommission_storno_sales_sum',
        'сommission_correct_sales_sum',
        'сommission_returns_sum',
        'сommission_storno_returns_sum',
        'сommission_correct_returns_sum',
        'сommission_marriage_payment_sum',
        'сommission_payment_lost_marriage_sum',
        'сommission_partial_compensation_marriage_sum',
        'сommission_advance_payment_goods_without_payment_sum',
        'sales_quantity_sum',
        'strono_sales_quantity_sum',
        'correct_sales_quantity_sum',
        'returns_quantity_sum',
        'strono_returns_quantity_sum',
        'correct_return_quantity_sum',
        'marriage_payment_quantity_sum',
        'payment_lost_marriage_quantity_sum',
        'partial_compensation_marriage_quantity_sum',
        'advance_payment_goods_without_payment_quantity_sum',
        'retail_sales_sum',
        'retail_return_sum',
        'retail_storno_sales_sum',
        'retail_correct_sales_sum',
        'retail_storno_returns_sum',
        'retail_correct_returns_sum',
        'retail_marriage_payment_sum',
        'retail_payment_lost_marriage_sum',
        'retail_partial_compensation_marriage_sum',
        'retail_advance_payment_goods_without_payment_sum',
    ]
    filter_names = [
        'Продажа',
        'Возврат',
        'Сторно продаж',
        'Корректная продажа',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Продажа',
        'Возврат',
        'Сторно продаж',
        'Корректная продажа',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
    ]
    aggregate_fields_names = [
        *['retail_price_withdisc_rub'] * 10,
        *['ppvz_for_pay'] * 10,
        *['quantity'] * 10,
        *['retail_amount'] * 10
    ]
    net_costs_argument_names = [
        'netcost_sale_sum',
        'netcost_storno_sale_sum',
        'netcost_correct_sale_sum',
        'netcost_return_sum',
        'net_cost_strono_returns_sum',
        'net_cost_correct_return_sum',
        'net_cost_marriage_payment_sum',
        'net_cost_payment_lost_marriage_sum',
        'net_cost_partial_compensation_marriage_sum',
        'net_cost_advance_payment_goods_without_payment_sum'
    ]
    net_costs_filter_names = [
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения'
    ]
    tax_rates_argument_names = [
        'tax_sale_sum',
        'tax_storno_sale_sum',
        'tax_correct_sale_sum',
        'tax_return_sum',
        'tax_storno_return_sum',
        'tax_correct_return_sum',
        'tax_marriage_payment_sum',
        'tax_payment_lost_marriage_sum',
        'tax_cost_partial_compensation_marriage_sum',
        'tax_cost_advance_payment_goods_without_payment_sum'
    ]
    tax_rates_filter_names = [
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения'
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
