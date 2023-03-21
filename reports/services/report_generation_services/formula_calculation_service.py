"""
WARNING: the order in which the data is transmitted is IMPORTANT
"""


def calculate_revenue(
        sales_sum: float,
        returns_sum: float,
        storno_sales_sum: float,
        correct_sales_sum: float,
        storno_returns_sum: float,
        correct_returns_sum: float,
        marriage_payment_sum,
        payment_lost_marriage_sum
):
    revenue: float = (
            sales_sum - storno_sales_sum + correct_sales_sum - returns_sum +
            storno_returns_sum - correct_returns_sum + marriage_payment_sum + payment_lost_marriage_sum
    )

    return revenue


def calculate_sales_quantity(
        sales_quantity_sum: float,
        strono_sales_quantity_sum: float,
        correct_sales_quantity_sum: float,
        marriage_payment_sum,
        payment_lost_marriage_sum
):
    sales_quantity: float = (
            sales_quantity_sum - strono_sales_quantity_sum + correct_sales_quantity_sum +
            marriage_payment_sum + payment_lost_marriage_sum
    )

    return sales_quantity


def calculate_returns_quantity(
        returns_quantity_sum: float,
        strono_returns_quantity_sum: float,
        correct_return_quantity_sum: float
):
    returns_quantity: float = (returns_quantity_sum + strono_returns_quantity_sum - correct_return_quantity_sum)

    return returns_quantity


def calculate_commission(
        sales_sum: float,
        commission_sales_sum: float,
        returns_sum: float,
        commission_returns_sum: float,
        storno_sales_sum: float,
        commission_storno_sales_sum: float,
        storno_returns_sum: float,
        commission_storno_returns_sum: float,
        correct_sales_sum: float,
        commission_correct_sales_sum: float,
        correct_returns_sum: float,
        commission_correct_returns_sum: float,
        marriage_payment_sum,
        payment_lost_marriage_sum,
        commission_marriage_payment_sum: float,
        commission_payment_lost_marriage_sum: float
):
    commission: float = (
            (sales_sum - storno_sales_sum + correct_sales_sum - returns_sum +
             storno_returns_sum - correct_returns_sum + marriage_payment_sum + payment_lost_marriage_sum) -
            (commission_sales_sum - commission_storno_sales_sum + commission_correct_sales_sum -
             commission_returns_sum + commission_storno_returns_sum - commission_correct_returns_sum +
             commission_marriage_payment_sum + commission_payment_lost_marriage_sum)
    )

    return commission


def calculate_logistics(logistic_sum):
    return logistic_sum


def calculate_supplier_costs(supplier_costs_sum: float):
    return supplier_costs_sum


def calculate_tax_value(
        tax_sale_sum: float,
        tax_storno_sale_sum: float,
        tax_correct_sale_sum: float,
        tax_return_sum: float,
        tax_storno_return_sum: float,
        tax_correct_return_sum: float,
        tax_marriage_payment_sum,
        tax_payment_lost_marriage_sum
):
    tax_value: float = (
            tax_sale_sum - tax_storno_sale_sum + tax_correct_sale_sum -
            tax_return_sum + tax_storno_return_sum - tax_correct_return_sum +
            tax_marriage_payment_sum + tax_payment_lost_marriage_sum
    )

    return tax_value


def calculate_net_costs(
        netcost_sale_sum: float,
        netcost_storno_sale_sum: float,
        netcost_correct_sale_sum: float,
        netcost_return_sum: float,
        net_cost_strono_returns_sum: float,
        net_cost_correct_return_sum: float,
        net_cost_marriage_payment_sum,
        net_cost_payment_lost_marriage_sum
):
    net_costs: float = (
            netcost_sale_sum - netcost_storno_sale_sum + netcost_correct_sale_sum -
            netcost_return_sum + net_cost_strono_returns_sum - net_cost_correct_return_sum +
            net_cost_marriage_payment_sum + net_cost_payment_lost_marriage_sum
    )

    return net_costs


def calculate_marginality(net_costs_sum: float, revenue: float):
    if net_costs_sum > 0:
        return ((revenue - net_costs_sum) / revenue) * 100 if revenue > 0 else 0

    return net_costs_sum


def calculate_profit(
        penalty_sum: float,
        additional_payment_sum: float,
        wb_costs_sum: float,
        revenue: float,
        net_costs: float,
        commission: float,
        logistics: float,
        tax_value: float,
        supplier_costs_sum: float
):
    profit: float = (
            revenue - net_costs - commission -
            logistics - penalty_sum - additional_payment_sum -
            wb_costs_sum - tax_value - supplier_costs_sum
    )

    return profit


def calculate_profitability(
        profit: float,
        revenue: float
):
    return (profit / revenue) * 100 if revenue > 0 else 0


def calculate_share_in_revenue(
        revenue_by_obj: float,
        total_revenue: float
):
    return (revenue_by_obj / total_revenue) * 100 if total_revenue > 0 else 0
