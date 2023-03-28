from decimal import Decimal

from reports.services.handle_graphs_filter_data import get_period_filter_data
import pytest

from reports.services.report_generation_services.formula_calculation_service import calculate_revenue, \
    calculate_sales_quantity, calculate_returns_quantity, calculate_commission, calculate_logistics, \
    calculate_supplier_costs, calculate_tax_value, calculate_net_costs, calculate_marginality, calculate_profit, \
    calculate_profitability, calculate_share_in_revenue
from reports.services.report_generation_services.get_total_financials_service import get_total_financials
from reports.services.report_generation_services.handling_calculated_financial_by_weeks_service import \
    get_calculated_financials_by_weeks
from reports.services.report_generation_services.handling_calculated_finfancials_by_products_service import \
    get_calculated_financials_by_products
from reports.tests.reports_pytest_fixtures import test_sale_objects_by_weeks, \
    test_supplier_costs_sum_list, test_wb_costs_sum_list, test_sale_objects_by_products


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


def test_get_total_financials(test_sale_objects_by_weeks, test_supplier_costs_sum_list, test_wb_costs_sum_list):
    totals = get_total_financials(test_sale_objects_by_weeks, test_supplier_costs_sum_list, test_wb_costs_sum_list)

    test_expected_totals = {
        "revenue_total": 4812188.739999999,
        "sales_amount_total": 17888.0,
        "returns_amount_total": 76.0,
        "logistics_total": 1455521,
        "net_costs_sum_total": 67505,
        "marginality_total": 99,
        "commission_total": 944565,
        "supplier_costs_total": 1354,
        "wb_costs_total": 9366,
        "tax_total": 577463,
        "profit_total": 2208334,
        "profitability_total": 46,
        "penalty_total": 22858,
        "additional_payment_sum_total": 15154,
    }

    assert totals.get('revenue_total') == test_expected_totals.get('revenue_total')
    assert totals.get('sales_amount_total') == test_expected_totals.get('sales_amount_total')
    assert totals.get('returns_amount_total') == test_expected_totals.get('returns_amount_total')
    assert totals.get('logistics_total') == test_expected_totals.get('logistics_total')
    assert totals.get('net_costs_sum_total') == test_expected_totals.get('net_costs_sum_total')
    assert totals.get('marginality_total') == test_expected_totals.get('marginality_total')
    assert totals.get('commission_total') == test_expected_totals.get('commission_total')
    assert totals.get('supplier_costs_total') == test_expected_totals.get('supplier_costs_total')
    assert totals.get('wb_costs_total') == test_expected_totals.get('wb_costs_total')
    assert totals.get('tax_total') == test_expected_totals.get('tax_total')
    assert totals.get('profit_total') == test_expected_totals.get('profit_total')
    assert totals.get('profitability_total') == test_expected_totals.get('profitability_total')
    assert totals.get('penalty_total') == test_expected_totals.get('penalty_total')
    assert totals.get('additional_payment_sum_total') == test_expected_totals.get('additional_payment_sum_total')


def test_get_calculated_financials_by_weeks(
        test_sale_objects_by_weeks,
        test_supplier_costs_sum_list,
        test_wb_costs_sum_list
):
    financials_by_week = get_calculated_financials_by_weeks(
        test_sale_objects_by_weeks[1], test_supplier_costs_sum_list[1], test_wb_costs_sum_list[1])

    test_expected_financials_by_week = {
        "date_from": "05.12.2022",
        "date_to": "11.12.2022",
        "week_num": 49,
        "revenue": 203309.36,
        "sales_amount": 1036.0,
        "returns_amount": 2.0,
        "logistics": 38458.560000000005,
        "net_costs_sum": 20587.0,
        "marginality": 89.87405203577444,
        "commission": 44715.6899999984,
        "supplier_costs": 0.0,
        "wb_costs": 0.0,
        "tax": 24397.123199999896,
        "profit": 93880.98679999997,
        "profitability": 46.17642139053508,
        "penalty": 2160.0,
        "additional_payment_sum": 420.0,
    }

    assert financials_by_week == test_expected_financials_by_week


def test_get_calculated_financials_by_products(test_sale_objects_by_products):
    financials_by_products = [
        get_calculated_financials_by_products(
            sale,
            4812188.739999999) for sale in test_sale_objects_by_products]

    test_expected_financials_by_products = [
        {
            "nm_id": 51897113,
            "image": "https://basket-04.wb.ru/vol518/part51897/51897113/images/tm/1.jpg",
            "sales_quantity_value": 33,
            "returns_quantity_value": 0,
            "revenue_by_article": 22320,
            "share_in_profits": 0.46,
            "product_marginality": 82,
        },
        {
            "nm_id": 51897115,
            "image": "https://basket-04.wb.ru/vol518/part51897/51897115/images/tm/1.jpg",
            "sales_quantity_value": 11,
            "returns_quantity_value": 0,
            "revenue_by_article": 3670,
            "share_in_profits": 0.08,
            "product_marginality": 30,
        },
        {
            "nm_id": 51897116,
            "image": "https://basket-04.wb.ru/vol518/part51897/51897116/images/tm/1.jpg",
            "sales_quantity_value": 4,
            "returns_quantity_value": 0,
            "revenue_by_article": 1291,
            "share_in_profits": 0.03,
            "product_marginality": -279,
        },
    ]

    assert financials_by_products == test_expected_financials_by_products






