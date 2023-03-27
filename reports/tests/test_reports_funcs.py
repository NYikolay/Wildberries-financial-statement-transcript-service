from decimal import Decimal

from reports.services.handle_graphs_filter_data import get_period_filter_data
import pytest

from reports.services.report_generation_services.formula_calculation_service import calculate_revenue, \
    calculate_sales_quantity, calculate_returns_quantity, calculate_commission, calculate_logistics, \
    calculate_supplier_costs, calculate_tax_value, calculate_net_costs, calculate_marginality, calculate_profit, \
    calculate_profitability, calculate_share_in_revenue


def test_get_period_filter_data():
    filter_dict = {
        '2022': ['52,51,50,49,48'],
        '2023': ['11,10,9,8,7,5,4,3,1']
    }

    expected_filter_list = [
        {'year': 2022, 'week_nums': [52, 51, 50, 49, 48]},
        {'year': 2023, 'week_nums': [11, 10, 9, 8, 7, 5, 4, 3, 1]}
    ]

    filter_list = get_period_filter_data(filter_dict)

    assert expected_filter_list == filter_list


def test_fail_period_filter_data():
    filter_dict = {
        '2022': ['5as2,51,50,49,48'],
        '2023': ['11,10,9,8,7,5as,4,3,1']
    }
    with pytest.raises(Exception):
        get_period_filter_data(filter_dict)


def test_calculate_revenue():
    revenue = calculate_revenue(
        458656.9399999999,
        5433.27,
        18430.0,
        20773.0,
        700.0,
        700.0,
        3936.5900000000006,
        709.0
    )

    assert round(revenue) == round(460212.25999999999)


def test_calculate_sales_quantity():
    sales_quantity = calculate_sales_quantity(
        260.0,
        28.0,
        29.0,
        2.0,
        0.0
    )
    assert sales_quantity == 263.0


def test_calculate_returns_quantity():
    returns_quantity = calculate_returns_quantity(
        16.0,
        2.0,
        2.0
    )

    assert returns_quantity == 16.0


def test_calculate_commission():
    commission = calculate_commission(
        224122.34999999826,
        183141.66000000003,
        530.61,
        433.54,
        109296.90999999964,
        93636.75000000023,
        701.22,
        602.26,
        109296.90999999964,
        89777.5900000001,
        701.22,
        575.17,
        1027.6200000000001,
        0.0,
        1027.6200000000001,
        0.0
    )

    assert commission == 44715.6899999984


def test_calculate_logistics():
    logistics = calculate_logistics(12332.12121)

    assert logistics == 12332.12121


def test_calculate_supplier_costs():
    supplier_costs = calculate_supplier_costs(12111.4222)

    assert supplier_costs == 12111.4222


def test_calculate_tax_value():
    tax = calculate_tax_value(
        24330.208799999902,
        12192.423599999982,
        12192.42359999998,
        56.400000000000006,
        84.0,
        84.0,
        123.31440000000002,
        0.0
    )

    assert tax == 24397.123199999896


def test_calculate_net_costs():
    net_costs_sum = calculate_net_costs(
        4026.0,
        122.0,
        122.0,
        322.0,
        111.0,
        555.0,
        112.0,
        554.0,
    )

    assert net_costs_sum == 3926.0


def test_calculate_marginality_without_net_costs():
    marginality = calculate_marginality(
        0,
        1222.2
    )

    assert marginality == 0


def test_calculate_marginality_with_net_costs():
    marginality = calculate_marginality(
        31926.0,
        4812189.112
    )

    assert marginality == 99.3365597390928


def test_calculate_marginality_without_revenue():
    marginality = calculate_marginality(
        3926.0,
        0
    )

    assert marginality == 0


def test_calculate_profit():
    profit = calculate_profit(
        18287.97,
        1968.0,
        0.0,
        247857.01999999833,
        4097.0,
        44082.689999998605,
        47432.36999999996,
        27599.263199999943,
        0.0
    )

    assert profit == 104389.72679999981


def test_calculate_profitability_without_revenue():
    profitability = calculate_profitability(
        104389.72679999981,
        0
    )

    assert profitability == 0


def test_calculate_profitability_with_revenue():
    profitability = calculate_profitability(
        104389.72679999981,
        460212.25999999912
    )

    assert profitability == 22.682952166463362


def test_calculate_share_in_revenue_without_revenue():
    share_in_revenue = calculate_share_in_revenue(
        104389.72679999981,
        0
    )

    assert share_in_revenue == 0


def test_calculate_share_in_revenue_with_revenue():
    share_in_revenue = calculate_share_in_revenue(
        104389.72679999981,
        461212.25999999912
    )

    assert share_in_revenue == 22.63377101033698




