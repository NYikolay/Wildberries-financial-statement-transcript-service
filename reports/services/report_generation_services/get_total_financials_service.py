
import json

from reports.services.report_generation_services.formula_calculation_service import calculate_marginality, \
    calculate_profitability
from reports.services.report_generation_services.handling_calculated_financial_by_weeks_service import \
    get_calculated_financials_by_weeks


def get_total_financials(sale_objects_by_weeks, supplier_costs_sum_list, wb_costs_sum_list) -> dict:
    """
    The function forms the final data set for the report by summing the values obtained
    from the function get_calculated_financials_by_weeks
    :param sale_objects_by_weeks: QuerySet(), consisting of annotated and aggregated data from the SaleObject model.
    Presented as a list containing dictionaries (List[dict])
    :param supplier_costs_sum_list: QuerySet(), consisting of annotated and aggregated data from the SaleReport model.
    Presented as a list containing dictionaries (List[dict])
    :param wb_costs_sum_list: QuerySet(), consisting of annotated and aggregated data from the SaleReport model.
    Presented as a list containing dictionaries (List[dict])
    :return:
    """

    revenue_total = []
    retail_amount_revenue_total = []
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

    for inter_data, supplier_cost, wb_cost in zip(sale_objects_by_weeks, supplier_costs_sum_list, wb_costs_sum_list):
        calculated_financials: dict = get_calculated_financials_by_weeks(inter_data, supplier_cost, wb_cost)
        reports_by_week.append(calculated_financials)
        revenue_total.append(calculated_financials.get('revenue'))
        retail_amount_revenue_total.append(calculated_financials.get('retail_amount_revenue'))
        sales_amount_total.append(calculated_financials.get('sales_amount'))
        returns_amount_total.append(calculated_financials.get('returns_amount'))
        logistics_total.append(calculated_financials.get('logistics'))
        net_costs_sum_total.append(calculated_financials.get('net_costs_sum'))
        commission_total.append(calculated_financials.get('commission'))
        supplier_costs_total.append(calculated_financials.get('supplier_costs'))
        wb_costs_total.append(calculated_financials.get('wb_costs'))
        marginality_total.append(calculated_financials.get('marginality'))
        tax_total.append(calculated_financials.get('tax'))
        profit_total.append(calculated_financials.get('profit'))
        profitability_total.append(calculated_financials.get('profitability'))
        penalty_total.append(calculated_financials.get('penalty'))
        additional_payment_sum_total.append(calculated_financials.get('additional_payment_sum'))

    marginality = calculate_marginality(sum(net_costs_sum_total), sum(retail_amount_revenue_total))
    profitability_total = calculate_profitability(sum(profit_total), sum(retail_amount_revenue_total))

    return {
        'revenue_total': sum(retail_amount_revenue_total),
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
        'profitability_total': round(profitability_total),
        'reports_by_week': json.dumps(reports_by_week, ensure_ascii=False),
        'penalty_total': round(sum(penalty_total)),
        'additional_payment_sum_total': round(sum(additional_payment_sum_total))
    }