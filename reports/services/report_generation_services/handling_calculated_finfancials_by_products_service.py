import json

from reports.services.report_generation_services.formula_calculation_service import (
    calculate_marginality,
    calculate_sales_quantity,
    calculate_returns_quantity,
    calculate_revenue,
    calculate_share_in_revenue,
    calculate_net_costs
)


def get_calculated_financials_by_products(sales_objects_by_product_figures, revenue_total: float) -> dict:
    """
    WARNING! The order in which the values are transmitted is very important
    CALCULATIONS ARE NOT ROUNDED, ROUNDING ONLY WHEN RETURNING TO THE USER
    Based on the results of sales aggregations, it calculates and returns user-ready figures.
    :param sales_objects_by_product_figures:
    :param revenue_total:
    :return:
    """

    sales_quantity_value: float = calculate_sales_quantity(
        sales_objects_by_product_figures.get('sales_quantity_sum'),
        sales_objects_by_product_figures.get('strono_sales_quantity_sum'),
        sales_objects_by_product_figures.get('correct_sales_quantity_sum'),
        sales_objects_by_product_figures.get('marriage_payment_quantity_sum'),
        sales_objects_by_product_figures.get('payment_lost_marriage_quantity_sum'),
        sales_objects_by_product_figures.get('partial_compensation_marriage_quantity_sum'),
        sales_objects_by_product_figures.get('advance_payment_goods_without_payment_quantity_sum')
    )

    returns_quantity_value: float = calculate_returns_quantity(
        sales_objects_by_product_figures.get('returns_quantity_sum'),
        sales_objects_by_product_figures.get('strono_returns_quantity_sum'),
        sales_objects_by_product_figures.get('correct_return_quantity_sum')
    )

    revenue_by_article: float = calculate_revenue(
        sales_objects_by_product_figures.get('retail_sales_sum'),
        sales_objects_by_product_figures.get('retail_return_sum'),
        sales_objects_by_product_figures.get('retail_storno_sales_sum'),
        sales_objects_by_product_figures.get('retail_correct_sales_sum'),
        sales_objects_by_product_figures.get('retail_storno_returns_sum'),
        sales_objects_by_product_figures.get('retail_correct_returns_sum'),
        sales_objects_by_product_figures.get('retail_marriage_payment_sum'),
        sales_objects_by_product_figures.get('retail_payment_lost_marriage_sum'),
        sales_objects_by_product_figures.get('retail_partial_compensation_marriage_sum'),
        sales_objects_by_product_figures.get('retail_advance_payment_goods_without_payment_sum')
    )

    share_in_profits: float = calculate_share_in_revenue(
        revenue_by_article,
        revenue_total
    )

    net_costs_sum: float = calculate_net_costs(
        sales_objects_by_product_figures.get('netcost_sale_sum'),
        sales_objects_by_product_figures.get('netcost_storno_sale_sum'),
        sales_objects_by_product_figures.get('netcost_correct_sale_sum'),
        sales_objects_by_product_figures.get('netcost_return_sum'),
        sales_objects_by_product_figures.get('net_cost_strono_returns_sum'),
        sales_objects_by_product_figures.get('net_cost_correct_return_sum'),
        sales_objects_by_product_figures.get('net_cost_marriage_payment_sum'),
        sales_objects_by_product_figures.get('net_cost_payment_lost_marriage_sum'),
        sales_objects_by_product_figures.get('net_cost_partial_compensation_marriage_sum'),
        sales_objects_by_product_figures.get('net_cost_advance_payment_goods_without_payment_sum')
    )

    marginality = calculate_marginality(
        net_costs_sum,
        revenue_by_article
    )

    product_total_financials = {
        'nm_id': sales_objects_by_product_figures.get('nm_id'),
        'image': sales_objects_by_product_figures.get('image'),
        'sales_quantity_value': round(sales_quantity_value),
        'returns_quantity_value': round(returns_quantity_value),
        'revenue_by_article': round(revenue_by_article),
        'share_in_profits': round(share_in_profits, 2),
        'product_marginality': round(marginality),
    }

    return product_total_financials
