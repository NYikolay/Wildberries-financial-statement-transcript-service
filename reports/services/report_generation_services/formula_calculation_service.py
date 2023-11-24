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
        marriage_payment_sum: float,
        sales_payment_lost_marriage_sum: float,
        returns_payment_lost_marriage_sum: float,
        partial_compensation_marriage_sum: float,
        sales_advance_payment_goods_without_payment_sum: float,
        returns_advance_payment_goods_without_payment_sum: float,
        compensation_for_subs_goods_sum: float
) -> float:

    revenue: float = (
            sales_sum - storno_sales_sum + correct_sales_sum - returns_sum +
            storno_returns_sum - correct_returns_sum + marriage_payment_sum + sales_payment_lost_marriage_sum -
            returns_payment_lost_marriage_sum + partial_compensation_marriage_sum +
            sales_advance_payment_goods_without_payment_sum - returns_advance_payment_goods_without_payment_sum +
            compensation_for_subs_goods_sum
    )

    return revenue


def calculate_sales_quantity(
        sales_quantity_sum: float,
        strono_sales_quantity_sum: float,
        correct_sales_quantity_sum: float,
        marriage_payment_sum: float,
        sales_payment_lost_marriage_sum: float,
        returns_payment_lost_marriage_sum: float,
        partial_compensation_marriage_sum: float,
        sales_advance_payment_goods_without_payment_sum: float,
        returns_advance_payment_goods_without_payment_sum: float,
        quantity_compensation_for_subs_goods: float
):

    sales_quantity: float = (
            sales_quantity_sum - strono_sales_quantity_sum + correct_sales_quantity_sum +
            marriage_payment_sum + sales_payment_lost_marriage_sum - returns_payment_lost_marriage_sum +
            partial_compensation_marriage_sum + sales_advance_payment_goods_without_payment_sum -
            returns_advance_payment_goods_without_payment_sum + quantity_compensation_for_subs_goods
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
        marriage_payment_sum: float,
        sales_payment_lost_marriage_sum: float,
        returns_payment_lost_marriage_sum: float,
        commission_marriage_payment_sum: float,
        commission_sales_payment_lost_marriage_sum: float,
        commission_returns_payment_lost_marriage_sum: float,
        partial_compensation_marriage_sum: float,
        sales_advance_payment_goods_without_payment_sum: float,
        returns_advance_payment_goods_without_payment_sum: float,
        commission_partial_compensation_marriage_sum: float,
        commission_sales_advance_payment_goods_without_payment_sum: float,
        commission_returns_advance_payment_goods_without_payment_sum: float,
        commission_reimbursement_of_transportation_costs: float,
        commission_overstatement_of_logistics_costs: float,
        compensation_for_subs_goods_sum: float,
        commission_compensation_for_subs_goods: float

):

    commission: float = (
            (sales_sum - storno_sales_sum + correct_sales_sum - returns_sum +
             storno_returns_sum - correct_returns_sum + marriage_payment_sum + sales_payment_lost_marriage_sum -
             returns_payment_lost_marriage_sum + partial_compensation_marriage_sum +
             sales_advance_payment_goods_without_payment_sum - returns_advance_payment_goods_without_payment_sum) -
            (commission_sales_sum - commission_storno_sales_sum + commission_correct_sales_sum -
             commission_returns_sum + commission_storno_returns_sum - commission_correct_returns_sum +
             commission_marriage_payment_sum + commission_sales_payment_lost_marriage_sum -
             commission_returns_payment_lost_marriage_sum + commission_partial_compensation_marriage_sum +
             commission_sales_advance_payment_goods_without_payment_sum -
             commission_returns_advance_payment_goods_without_payment_sum) -
            (commission_reimbursement_of_transportation_costs + commission_overstatement_of_logistics_costs) +
            (compensation_for_subs_goods_sum - commission_compensation_for_subs_goods)
    )

    return commission


def calculate_logistics(logistic_sum: float):
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
        tax_marriage_payment_sum: float,
        tax_sales_payment_lost_marriage_sum: float,
        tax_returns_payment_lost_marriage_sum: float,
        tax_cost_partial_compensation_marriage_sum: float,
        tax_cost_sales_advance_payment_goods_without_payment_sum: float,
        tax_cost_returns_advance_payment_goods_without_payment_sum: float,
        tax_compensation_for_subs_goods: float
):
    tax_value: float = (
            tax_sale_sum - tax_storno_sale_sum + tax_correct_sale_sum -
            tax_return_sum + tax_storno_return_sum - tax_correct_return_sum +
            tax_marriage_payment_sum + tax_sales_payment_lost_marriage_sum - tax_returns_payment_lost_marriage_sum +
            tax_cost_partial_compensation_marriage_sum + tax_cost_sales_advance_payment_goods_without_payment_sum -
            tax_cost_returns_advance_payment_goods_without_payment_sum + tax_compensation_for_subs_goods
    )

    return tax_value


def calculate_net_costs(
        net_cost_sale_sum: float,
        net_cost_storno_sale_sum: float,
        net_cost_correct_sale_sum: float,
        net_cost_return_sum: float,
        net_cost_strono_returns_sum: float,
        net_cost_correct_return_sum: float,
        net_cost_marriage_payment_sum: float,
        net_cost_sales_payment_lost_marriage_sum: float,
        net_cost_returns_payment_lost_marriage_sum: float,
        net_cost_partial_compensation_marriage_sum: float,
        net_cost_sales_advance_payment_goods_without_payment_sum: float,
        net_cost_returns_advance_payment_goods_without_payment_sum: float,
        net_cost_compensation_for_subs_goods: float

):
    net_costs: float = (
            net_cost_sale_sum - net_cost_storno_sale_sum + net_cost_correct_sale_sum -
            net_cost_return_sum + net_cost_strono_returns_sum - net_cost_correct_return_sum +
            net_cost_marriage_payment_sum + net_cost_sales_payment_lost_marriage_sum -
            net_cost_returns_payment_lost_marriage_sum +
            net_cost_partial_compensation_marriage_sum + net_cost_sales_advance_payment_goods_without_payment_sum -
            net_cost_returns_advance_payment_goods_without_payment_sum + net_cost_compensation_for_subs_goods
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


def calculate_rom(total_payable: float, net_costs_sum: float):
    if net_costs_sum > 0 and total_payable > 0:
        return (total_payable / net_costs_sum) * 100

    return 0


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


def calculate_total_payable(
        revenue: float,
        commission: float,
        logistics: float,
        penalty_sum: float,
        additional_payment_sum: float
):

    total_payable: float = (revenue - commission - logistics - penalty_sum - additional_payment_sum)

    return total_payable