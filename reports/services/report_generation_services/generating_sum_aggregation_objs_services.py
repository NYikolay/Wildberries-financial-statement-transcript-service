from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Coalesce

from reports.services.report_generation_services.db_annotation_formulas_services import \
    get_retail_revenue_formula_annotation_obj, get_revenue_formula_annotation_obj, \
    get_share_in_revenue_formula_annotation_obj, get_sales_quantity_formula_annotation_obj, \
    get_returns_quantity_formula_annotation_obj, get_commission_formula_annotation_obj, \
    get_net_costs_formula_annotation_obj, get_marginality_formula_annotation_obj, \
    get_share_in_number_formula_annotation_obj, get_total_payable_formula_annotation_obj, get_rom_formula_annotation_obj


def get_financials_annotation_objects() -> dict:
    revenue = get_retail_revenue_formula_annotation_obj()
    interim_revenue = get_revenue_formula_annotation_obj()
    share_in_revenue = get_share_in_revenue_formula_annotation_obj()
    sales_amount = get_sales_quantity_formula_annotation_obj()
    returns_amount = get_returns_quantity_formula_annotation_obj()
    commission = get_commission_formula_annotation_obj()
    net_costs_sum = get_net_costs_formula_annotation_obj()
    product_marginality = get_marginality_formula_annotation_obj()
    share_in_number = get_share_in_number_formula_annotation_obj()
    total_payable = get_total_payable_formula_annotation_obj()
    rom = get_rom_formula_annotation_obj()

    return {
        "revenue": revenue,
        "interim_revenue": interim_revenue,
        "share_in_revenue": share_in_revenue,
        "net_costs_sum": net_costs_sum,
        "product_marginality": product_marginality,
        "share_in_number": share_in_number,
        'sales_amount': sales_amount,
        'returns_amount': returns_amount,
        'commission': commission,
        'total_payable': total_payable,
        'rom': rom
    }


def get_product_financials_annotations_objects() -> dict:
    revenue = get_retail_revenue_formula_annotation_obj()
    interim_revenue = get_revenue_formula_annotation_obj()
    sales_amount = get_sales_quantity_formula_annotation_obj()
    returns_amount = get_returns_quantity_formula_annotation_obj()
    commission = get_commission_formula_annotation_obj()
    net_costs_sum = get_net_costs_formula_annotation_obj()
    product_marginality = get_marginality_formula_annotation_obj()
    total_payable = get_total_payable_formula_annotation_obj()
    rom = get_rom_formula_annotation_obj()

    return {
        "revenue": revenue,
        "interim_revenue": interim_revenue,
        "net_costs_sum": net_costs_sum,
        "marginality": product_marginality,
        'sales_amount': sales_amount,
        'returns_amount': returns_amount,
        'commission': commission,
        'total_payable': total_payable,
        'rom': rom
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
        'sales_payment_lost_marriage_sum',
        'returns_payment_lost_marriage_sum',
        'partial_compensation_marriage_sum',
        'sales_advance_payment_goods_without_payment_sum',
        'returns_advance_payment_goods_without_payment_sum',
        'reimbursement_of_transportation_costs',
        'overstatement_of_logistics_costs',
        'compensation_for_subs_goods_sum',
        'commission_sales_sum',
        'commission_storno_sales_sum',
        'commission_correct_sales_sum',
        'commission_returns_sum',
        'commission_storno_returns_sum',
        'commission_correct_returns_sum',
        'commission_marriage_payment_sum',
        'commission_sales_payment_lost_marriage_sum',
        'commission_returns_payment_lost_marriage_sum',
        'commission_partial_compensation_marriage_sum',
        'commission_sales_advance_payment_goods_without_payment_sum',
        'commission_returns_advance_payment_goods_without_payment_sum',
        'commission_reimbursement_of_transportation_costs',
        'commission_overstatement_of_logistics_costs',
        'commission_compensation_for_subs_goods',
        'sales_quantity_sum',
        'strono_sales_quantity_sum',
        'correct_sales_quantity_sum',
        'returns_quantity_sum',
        'strono_returns_quantity_sum',
        'correct_return_quantity_sum',
        'marriage_payment_quantity_sum',
        'sales_payment_lost_marriage_quantity_sum',
        'returns_payment_lost_marriage_quantity_sum',
        'partial_compensation_marriage_quantity_sum',
        'sales_advance_payment_goods_without_payment_quantity_sum',
        'returns_advance_payment_goods_without_payment_quantity_sum',
        'quantity_reimbursement_of_transportation_costs',
        'quantity_overstatement_of_logistics_costs',
        'quantity_compensation_for_subs_goods',
        'retail_sales_sum',
        'retail_return_sum',
        'retail_storno_sales_sum',
        'retail_correct_sales_sum',
        'retail_storno_returns_sum',
        'retail_correct_returns_sum',
        'retail_marriage_payment_sum',
        'retail_sales_payment_lost_marriage_sum',
        'retail_returns_payment_lost_marriage_sum',
        'retail_partial_compensation_marriage_sum',
        'retail_sales_advance_payment_goods_without_payment_sum',
        'retail_returns_advance_payment_goods_without_payment_sum',
        'retail_reimbursement_of_transportation_costs',
        'retail_overstatement_of_logistics_costs',
        'retail_compensation_for_subs_goods'
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
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Авансовая оплата за товар без движения',
        'Возмещение издержек по перевозке',
        'Перевыставление расходов по логистике',
        'Компенсация подмененного товара',
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Авансовая оплата за товар без движения',
        'Возмещение издержек по перевозке',
        'Перевыставление расходов по логистике',
        'Компенсация подмененного товара',
        'Продажа',
        'Сторно продаж',
        'Корректная продажа',
        'Возврат',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Авансовая оплата за товар без движения',
        'Возмещение издержек по перевозке',
        'Перевыставление расходов по логистике',
        'Компенсация подмененного товара',
        'Продажа',
        'Возврат',
        'Сторно продаж',
        'Корректная продажа',
        'Сторно возвратов',
        'Корректный возврат',
        'Оплата брака',
        'Оплата потерянного товара',
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Авансовая оплата за товар без движения',
        'Возмещение издержек по перевозке',
        'Перевыставление расходов по логистике',
        'Компенсация подмененного товара',
    ]
    aggregate_fields_names = [
        *['retail_price_withdisc_rub'] * 15,
        *['ppvz_for_pay'] * 15,
        *['quantity'] * 15,
        *['retail_amount'] * 15
    ]
    net_costs_argument_names = [
        'net_cost_sale_sum',
        'net_cost_storno_sale_sum',
        'net_cost_correct_sale_sum',
        'net_cost_return_sum',
        'net_cost_strono_returns_sum',
        'net_cost_correct_return_sum',
        'net_cost_marriage_payment_sum',
        'net_cost_sales_payment_lost_marriage_sum',
        'net_cost_returns_payment_lost_marriage_sum',
        'net_cost_partial_compensation_marriage_sum',
        'net_cost_sales_advance_payment_goods_without_payment_sum',
        'net_cost_returns_advance_payment_goods_without_payment_sum',
        'net_cost_compensation_for_subs_goods',
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
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Авансовая оплата за товар без движения',
        'Компенсация подмененного товара',
    ]
    tax_rates_argument_names = [
        'tax_sale_sum',
        'tax_storno_sale_sum',
        'tax_correct_sale_sum',
        'tax_return_sum',
        'tax_storno_return_sum',
        'tax_correct_return_sum',
        'tax_marriage_payment_sum',
        'tax_sales_payment_lost_marriage_sum',
        'tax_returns_payment_lost_marriage_sum',
        'tax_cost_partial_compensation_marriage_sum',
        'tax_cost_sales_advance_payment_goods_without_payment_sum',
        'tax_cost_returns_advance_payment_goods_without_payment_sum',
        'tax_compensation_for_subs_goods'
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
        'Оплата потерянного товара',
        'Частичная компенсация брака',
        'Авансовая оплата за товар без движения',
        'Авансовая оплата за товар без движения',
        'Компенсация подмененного товара',
    ]

    sum_aggregation_objs_dict = {}

    for arg_name, field_name, filter_name in zip(argument_names, aggregate_fields_names, filter_names):
        if filter_name == 'Авансовая оплата за товар без движения' or filter_name == 'Оплата потерянного товара':
            if 'sales' in arg_name:
                sum_aggregation_objs_dict[arg_name] = Coalesce(
                    Sum(field_name, filter=Q(supplier_oper_name=filter_name, doc_type_name='Продажа')),
                    0,
                    output_field=FloatField())
            elif 'returns' in arg_name:
                sum_aggregation_objs_dict[arg_name] = Coalesce(
                    Sum(field_name, filter=Q(supplier_oper_name=filter_name, doc_type_name='Возврат')),
                    0,
                    output_field=FloatField())
        else:
            sum_aggregation_objs_dict[arg_name] = Coalesce(
                Sum(field_name, filter=Q(supplier_oper_name=filter_name)), 0, output_field=FloatField()
            )

    net_costs_sum_aggregation_objs = {}

    for arg_name, filter_name in zip(net_costs_argument_names, net_costs_filter_names):
        if filter_name == 'Авансовая оплата за товар без движения' or filter_name == 'Оплата потерянного товара':
            if 'sales' in arg_name:
                net_costs_sum_aggregation_objs[arg_name] = Coalesce(
                    Sum('net_cost', filter=Q(supplier_oper_name=filter_name, doc_type_name='Продажа')),
                    0,
                    output_field=FloatField())
            elif 'returns' in arg_name:
                net_costs_sum_aggregation_objs[arg_name] = Coalesce(
                    Sum('net_cost', filter=Q(supplier_oper_name=filter_name, doc_type_name='Возврат')),
                    0,
                    output_field=FloatField())
        else:
            net_costs_sum_aggregation_objs[arg_name] = Coalesce(
                Sum('net_cost', filter=Q(supplier_oper_name=filter_name)), 0, output_field=FloatField()
            )

    tax_rates_sum_aggregation_objs = {}

    for arg_name, filter_name in zip(tax_rates_argument_names, tax_rates_filter_names):
        if filter_name == 'Авансовая оплата за товар без движения' or filter_name == 'Оплата потерянного товара':
            if 'sales' in arg_name:
                tax_rates_sum_aggregation_objs[arg_name] = Coalesce(
                    Sum('price_including_tax', filter=Q(supplier_oper_name=filter_name, doc_type_name='Продажа')),
                    0,
                    output_field=FloatField())
            elif 'returns' in arg_name:
                tax_rates_sum_aggregation_objs[arg_name] = Coalesce(
                    Sum('price_including_tax', filter=Q(supplier_oper_name=filter_name, doc_type_name='Возврат')),
                    0,
                    output_field=FloatField())
        else:
            tax_rates_sum_aggregation_objs[arg_name] = Coalesce(
                Sum('price_including_tax', filter=Q(supplier_oper_name=filter_name)), 0, output_field=FloatField()
            )

    return {
        'sum_aggregation_objs_dict': sum_aggregation_objs_dict,
        'net_costs_sum_aggregation_objs': net_costs_sum_aggregation_objs,
        'tax_rates_sum_aggregation_objs': tax_rates_sum_aggregation_objs
    }