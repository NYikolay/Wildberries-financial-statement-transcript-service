from reports.services.report_generation_services.formula_calculation_service import calculate_marginality, calculate_rom


def get_total_financials_by_barcode(sale_objects_by_weeks) -> dict:
    revenue_total = []
    rom_total = []
    sales_amount_total = []
    returns_amount_total = []
    logistics_total = []
    net_costs_sum_total = []
    commission_total = []
    penalty_total = []
    total_payable = []
    additional_payment_sum_total = []

    for sale_objects_by_week in sale_objects_by_weeks:
        revenue_total.append(sale_objects_by_week.get('revenue'))
        rom_total.append(sale_objects_by_week.get('rom'))
        sales_amount_total.append(sale_objects_by_week.get('sales_amount'))
        returns_amount_total.append(sale_objects_by_week.get('returns_amount'))
        logistics_total.append(sale_objects_by_week.get('logistics'))
        total_payable.append(sale_objects_by_week.get('total_payable'))
        net_costs_sum_total.append(sale_objects_by_week.get('net_costs_sum'))
        commission_total.append(sale_objects_by_week.get('commission'))
        penalty_total.append(sale_objects_by_week.get('penalty'))
        additional_payment_sum_total.append(sale_objects_by_week.get('additional_payment_sum'))

    net_costs_sum = sum(net_costs_sum_total)
    revenue = sum(revenue_total)
    total_payable_sum = sum(total_payable)

    marginality = calculate_marginality(net_costs_sum, revenue)
    rom = calculate_rom(total_payable_sum, net_costs_sum)

    return {
        'nm_id': sale_objects_by_weeks[0].get('nm_id'),
        'barcode': sale_objects_by_weeks[0].get('barcode'),
        'ts_name': sale_objects_by_weeks[0].get('ts_name'),
        'image': sale_objects_by_weeks[0].get('image'),
        'product_name': sale_objects_by_weeks[0].get('product_name'),
        'revenue_total': revenue,
        'sales_amount_total': sum(sales_amount_total),
        'returns_amount_total': sum(returns_amount_total),
        'logistics_total': round(sum(logistics_total)),
        'rom_total': round(rom),
        'total_payable': round(total_payable_sum),
        'net_costs_sum_total': round(net_costs_sum),
        'marginality_total': round(marginality),
        'commission_total': round(sum(commission_total)),
        'penalty_total': round(sum(penalty_total)),
        'additional_payment_sum_total': round(sum(additional_payment_sum_total))
    }
