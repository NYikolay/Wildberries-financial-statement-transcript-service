import json

from reports.services.report_generation_services.formula_calculation_service import calculate_revenue, \
    calculate_sales_quantity, calculate_returns_quantity, calculate_commission, calculate_logistics, \
    calculate_marginality, calculate_net_costs, calculate_total_payable


def get_calculated_financials_by_barcode_by_weeks(sales_object_figures: dict):
    revenue: float = calculate_revenue(
        sales_object_figures.get('sales_sum'),
        sales_object_figures.get('returns_sum'),
        sales_object_figures.get('storno_sales_sum'),
        sales_object_figures.get('correct_sales_sum'),
        sales_object_figures.get('storno_returns_sum'),
        sales_object_figures.get('correct_returns_sum'),
        sales_object_figures.get('marriage_payment_sum'),
        sales_object_figures.get('sales_payment_lost_marriage_sum'),
        sales_object_figures.get('returns_payment_lost_marriage_sum'),
        sales_object_figures.get('partial_compensation_marriage_sum'),
        sales_object_figures.get('sales_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('returns_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('compensation_for_subs_goods_sum')
    )

    retail_amount_revenue: float = calculate_revenue(
        sales_object_figures.get('retail_sales_sum'),
        sales_object_figures.get('retail_return_sum'),
        sales_object_figures.get('retail_storno_sales_sum'),
        sales_object_figures.get('retail_correct_sales_sum'),
        sales_object_figures.get('retail_storno_returns_sum'),
        sales_object_figures.get('retail_correct_returns_sum'),
        sales_object_figures.get('retail_marriage_payment_sum'),
        sales_object_figures.get('retail_sales_payment_lost_marriage_sum'),
        sales_object_figures.get('retail_returns_payment_lost_marriage_sum'),
        sales_object_figures.get('retail_partial_compensation_marriage_sum'),
        sales_object_figures.get('retail_sales_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('retail_returns_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('retail_compensation_for_subs_goods')
    )

    sales_quantity: float = calculate_sales_quantity(
        sales_object_figures.get('sales_quantity_sum'),
        sales_object_figures.get('strono_sales_quantity_sum'),
        sales_object_figures.get('correct_sales_quantity_sum'),
        sales_object_figures.get('marriage_payment_quantity_sum'),
        sales_object_figures.get('sales_payment_lost_marriage_quantity_sum'),
        sales_object_figures.get('returns_payment_lost_marriage_quantity_sum'),
        sales_object_figures.get('partial_compensation_marriage_quantity_sum'),
        sales_object_figures.get('sales_advance_payment_goods_without_payment_quantity_sum'),
        sales_object_figures.get('returns_advance_payment_goods_without_payment_quantity_sum'),
        sales_object_figures.get('quantity_compensation_for_subs_goods')
    )

    returns_quantity: float = calculate_returns_quantity(
        sales_object_figures.get('returns_quantity_sum'),
        sales_object_figures.get('strono_returns_quantity_sum'),
        sales_object_figures.get('correct_return_quantity_sum')
    )

    commission: float = calculate_commission(
        sales_object_figures.get('sales_sum'),
        sales_object_figures.get('commission_sales_sum'),
        sales_object_figures.get('returns_sum'),
        sales_object_figures.get('commission_returns_sum'),
        sales_object_figures.get('storno_sales_sum'),
        sales_object_figures.get('commission_storno_sales_sum'),
        sales_object_figures.get('storno_returns_sum'),
        sales_object_figures.get('commission_storno_returns_sum'),
        sales_object_figures.get('correct_sales_sum'),
        sales_object_figures.get('commission_correct_sales_sum'),
        sales_object_figures.get('correct_returns_sum'),
        sales_object_figures.get('commission_correct_returns_sum'),
        sales_object_figures.get('marriage_payment_sum'),
        sales_object_figures.get('sales_payment_lost_marriage_sum'),
        sales_object_figures.get('returns_payment_lost_marriage_sum'),
        sales_object_figures.get('commission_marriage_payment_sum'),
        sales_object_figures.get('commission_sales_payment_lost_marriage_sum'),
        sales_object_figures.get('commission_returns_payment_lost_marriage_sum'),
        sales_object_figures.get('partial_compensation_marriage_sum'),
        sales_object_figures.get('sales_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('returns_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('commission_partial_compensation_marriage_sum'),
        sales_object_figures.get('commission_sales_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('commission_returns_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('commission_reimbursement_of_transportation_costs'),
        sales_object_figures.get('commission_overstatement_of_logistics_costs'),
        sales_object_figures.get('compensation_for_subs_goods_sum'),
        sales_object_figures.get('commission_compensation_for_subs_goods'),
    )

    net_costs: float = calculate_net_costs(
        sales_object_figures.get('net_cost_sale_sum'),
        sales_object_figures.get('net_cost_storno_sale_sum'),
        sales_object_figures.get('net_cost_correct_sale_sum'),
        sales_object_figures.get('net_cost_return_sum'),
        sales_object_figures.get('net_cost_strono_returns_sum'),
        sales_object_figures.get('net_cost_correct_return_sum'),
        sales_object_figures.get('net_cost_marriage_payment_sum'),
        sales_object_figures.get('net_cost_sales_payment_lost_marriage_sum'),
        sales_object_figures.get('net_cost_returns_payment_lost_marriage_sum'),
        sales_object_figures.get('net_cost_partial_compensation_marriage_sum'),
        sales_object_figures.get('net_cost_sales_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('net_cost_returns_advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('net_cost_compensation_for_subs_goods')
    )

    logistics: float = calculate_logistics(sales_object_figures.get('logistic_sum'))

    marginality: float = calculate_marginality(net_costs, retail_amount_revenue)

    total_payable = calculate_total_payable(
        revenue,
        commission,
        logistics,
        sales_object_figures.get('penalty_sum'),
        sales_object_figures.get('additional_payment_sum')
    )

    return {
        'week_num': sales_object_figures.get('week_num'),
        'revenue': retail_amount_revenue,
        'sales_amount': sales_quantity,
        'returns_amount': returns_quantity,
        'logistics': logistics,
        'marginality': marginality,
        'net_costs_sum': net_costs,
        'commission': commission,
        'total_payable': total_payable,
        'penalty': sales_object_figures.get('penalty_sum'),
        'additional_payment_sum': sales_object_figures.get('additional_payment_sum')
    }


def get_total_financials_by_barcode(sale_objects_by_weeks) -> dict:
    revenue_total = []
    sales_amount_total = []
    returns_amount_total = []
    logistics_total = []
    net_costs_sum_total = []
    commission_total = []
    total_payable = []
    reports_by_week = {
        'week_nums': [],
        'revenues': [],
        'total_payable': []
    }
    penalty_total = []
    additional_payment_sum_total = []

    for sale_objects_by_week in sale_objects_by_weeks:
        calculated_financials: dict = get_calculated_financials_by_barcode_by_weeks(sale_objects_by_week)
        reports_by_week['week_nums'].append(calculated_financials.get('week_num'))
        reports_by_week['revenues'].append(calculated_financials.get('revenue'))
        reports_by_week['total_payable'].append(calculated_financials.get('total_payable'))
        revenue_total.append(calculated_financials.get('revenue'))
        total_payable.append(calculated_financials.get('total_payable'))
        sales_amount_total.append(calculated_financials.get('sales_amount'))
        returns_amount_total.append(calculated_financials.get('returns_amount'))
        logistics_total.append(calculated_financials.get('logistics'))
        net_costs_sum_total.append(calculated_financials.get('net_costs_sum'))
        commission_total.append(calculated_financials.get('commission'))
        penalty_total.append(calculated_financials.get('penalty'))
        additional_payment_sum_total.append(calculated_financials.get('additional_payment_sum'))

    marginality = calculate_marginality(sum(net_costs_sum_total), sum(revenue_total))

    return {
        'revenue_total': sum(revenue_total),
        'total_payable': round(sum(total_payable)),
        'sales_amount_total': sum(sales_amount_total),
        'returns_amount_total': sum(returns_amount_total),
        'logistics_total': round(sum(logistics_total)),
        'net_costs_sum_total': round(sum(net_costs_sum_total)),
        'marginality_total': round(marginality),
        'commission_total': round(sum(commission_total)),
        'reports_by_week': json.dumps(reports_by_week, ensure_ascii=False),
        'penalty_total': round(sum(penalty_total)),
        'additional_payment_sum_total': round(sum(additional_payment_sum_total))
    }