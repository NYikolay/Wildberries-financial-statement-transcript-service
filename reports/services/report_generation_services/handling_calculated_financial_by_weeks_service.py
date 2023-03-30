
from reports.services.report_generation_services.formula_calculation_service import (
    calculate_revenue, calculate_sales_quantity, calculate_returns_quantity, calculate_commission, calculate_logistics,
    calculate_supplier_costs, calculate_tax_value, calculate_net_costs, calculate_marginality, calculate_profit,
    calculate_profitability)


def get_calculated_financials_by_weeks(
        sales_object_figures: dict,
        supplier_costs_values: dict,
        sale_report_wb_costs_sum: dict,
) -> dict:
    """
    WARNING! The order in which the values are transmitted is very important
    CALCULATIONS ARE NOT ROUNDED, ROUNDING ONLY WHEN RETURNING TO THE USER
    Based on the results of sales aggregations, it calculates and returns user-ready figures.
    :param sales_object_figures: QuerySet(), consisting of annotated and aggregated data from the SaleObject model.
    Presented as a list containing dictionaries (List[dict])
    :param supplier_costs_values: QuerySet(), consisting of annotated and aggregated data from the SaleReport model.
    Presented as a list containing dictionaries (List[dict])
    :param sale_report_wb_costs_sum: QuerySet(), consisting of annotated and aggregated data from the SaleReport model.
    Presented as a list containing dictionaries (List[dict])
    :return:
    """

    revenue: float = calculate_revenue(
        sales_object_figures.get('sales_sum'),
        sales_object_figures.get('returns_sum'),
        sales_object_figures.get('storno_sales_sum'),
        sales_object_figures.get('correct_sales_sum'),
        sales_object_figures.get('storno_returns_sum'),
        sales_object_figures.get('correct_returns_sum'),
        sales_object_figures.get('marriage_payment_sum'),
        sales_object_figures.get('payment_lost_marriage_sum'),
        sales_object_figures.get('partial_compensation_marriage_sum'),
        sales_object_figures.get('advance_payment_goods_without_payment_sum')
    )

    retail_amount_revenue: float = calculate_revenue(
        sales_object_figures.get('retail_sales_sum'),
        sales_object_figures.get('retail_return_sum'),
        sales_object_figures.get('retail_storno_sales_sum'),
        sales_object_figures.get('retail_correct_sales_sum'),
        sales_object_figures.get('retail_storno_returns_sum'),
        sales_object_figures.get('retail_correct_returns_sum'),
        sales_object_figures.get('retail_marriage_payment_sum'),
        sales_object_figures.get('retail_payment_lost_marriage_sum'),
        sales_object_figures.get('retail_partial_compensation_marriage_sum'),
        sales_object_figures.get('retail_advance_payment_goods_without_payment_sum')
    )

    sales_quantity: float = calculate_sales_quantity(
        sales_object_figures.get('sales_quantity_sum'),
        sales_object_figures.get('strono_sales_quantity_sum'),
        sales_object_figures.get('correct_sales_quantity_sum'),
        sales_object_figures.get('marriage_payment_quantity_sum'),
        sales_object_figures.get('payment_lost_marriage_quantity_sum'),
        sales_object_figures.get('partial_compensation_marriage_quantity_sum'),
        sales_object_figures.get('advance_payment_goods_without_payment_quantity_sum')
    )

    returns_quantity: float = calculate_returns_quantity(
        sales_object_figures.get('returns_quantity_sum'),
        sales_object_figures.get('strono_returns_quantity_sum'),
        sales_object_figures.get('correct_return_quantity_sum')
    )

    commission: float = calculate_commission(
        sales_object_figures.get('sales_sum'),
        sales_object_figures.get('сommission_sales_sum'),
        sales_object_figures.get('returns_sum'),
        sales_object_figures.get('сommission_returns_sum'),
        sales_object_figures.get('storno_sales_sum'),
        sales_object_figures.get('сommission_storno_sales_sum'),
        sales_object_figures.get('storno_returns_sum'),
        sales_object_figures.get('сommission_storno_returns_sum'),
        sales_object_figures.get('correct_sales_sum'),
        sales_object_figures.get('сommission_correct_sales_sum'),
        sales_object_figures.get('correct_returns_sum'),
        sales_object_figures.get('сommission_correct_returns_sum'),
        sales_object_figures.get('marriage_payment_sum'),
        sales_object_figures.get('payment_lost_marriage_sum'),
        sales_object_figures.get('сommission_marriage_payment_sum'),
        sales_object_figures.get('сommission_payment_lost_marriage_sum'),
        sales_object_figures.get('partial_compensation_marriage_sum'),
        sales_object_figures.get('advance_payment_goods_without_payment_sum'),
        sales_object_figures.get('сommission_partial_compensation_marriage_sum'),
        sales_object_figures.get('сommission_advance_payment_goods_without_payment_sum')
    )

    logistics: float = calculate_logistics(sales_object_figures.get('logistic_sum'))

    supplier_costs_sum: float = calculate_supplier_costs(supplier_costs_values.get('supplier_costs_sum'))

    tax_value: float = calculate_tax_value(
        sales_object_figures.get('tax_sale_sum'),
        sales_object_figures.get('tax_storno_sale_sum'),
        sales_object_figures.get('tax_correct_sale_sum'),
        sales_object_figures.get('tax_return_sum'),
        sales_object_figures.get('tax_storno_return_sum'),
        sales_object_figures.get('tax_correct_return_sum'),
        sales_object_figures.get('tax_marriage_payment_sum'),
        sales_object_figures.get('tax_payment_lost_marriage_sum'),
        sales_object_figures.get('tax_cost_partial_compensation_marriage_sum'),
        sales_object_figures.get('tax_cost_advance_payment_goods_without_payment_sum')
    )

    net_costs: float = calculate_net_costs(
        sales_object_figures.get('netcost_sale_sum'),
        sales_object_figures.get('netcost_storno_sale_sum'),
        sales_object_figures.get('netcost_correct_sale_sum'),
        sales_object_figures.get('netcost_return_sum'),
        sales_object_figures.get('net_cost_strono_returns_sum'),
        sales_object_figures.get('net_cost_correct_return_sum'),
        sales_object_figures.get('net_cost_marriage_payment_sum'),
        sales_object_figures.get('net_cost_payment_lost_marriage_sum'),
        sales_object_figures.get('net_cost_partial_compensation_marriage_sum'),
        sales_object_figures.get('net_cost_advance_payment_goods_without_payment_sum')
    )

    marginality: float = calculate_marginality(net_costs, retail_amount_revenue)

    profit: float = calculate_profit(
        sales_object_figures.get('penalty_sum'),
        sales_object_figures.get('additional_payment_sum'),
        sale_report_wb_costs_sum.get('total_wb_costs_sum'),
        revenue,
        net_costs,
        commission,
        logistics,
        tax_value,
        supplier_costs_sum
    )

    profitability: float = calculate_profitability(profit, retail_amount_revenue)

    return {
        'date_from': sales_object_figures.get('date_from').strftime("%d.%m.%Y"),
        'date_to': sales_object_figures.get('date_to').strftime("%d.%m.%Y"),
        'week_num': sales_object_figures.get('week_num'),
        'revenue': retail_amount_revenue,
        'sales_amount': sales_quantity,
        'returns_amount': returns_quantity,
        'logistics': logistics,
        'net_costs_sum': net_costs,
        'marginality': marginality,
        'commission': commission,
        'supplier_costs': supplier_costs_sum,
        'wb_costs': sale_report_wb_costs_sum.get('total_wb_costs_sum'),
        'tax': tax_value,
        'profit': profit,
        'profitability': profitability,
        'penalty': sales_object_figures.get('penalty_sum'),
        'additional_payment_sum': sales_object_figures.get('additional_payment_sum')
    }
