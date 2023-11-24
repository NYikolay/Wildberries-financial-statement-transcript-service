import json
import datetime


def get_demo_dashboard_data():
    today = datetime.date.today()

    reports_by_week = [
        {
            "date_from": today.strftime('%Y-%m-%dT'), "date_to": today.strftime('%Y-%m-%dT'),
            "year": today.year, "week_num": today.isocalendar()[1],
            "revenue": 0.0, "sales_amount": 0.0, "returns_amount": 0.0,
            "logistics": 0.0, "net_costs_sum": 0.0, "marginality": 0.0,
            "commission": 0.0, "supplier_costs": 0.0, "wb_costs": 0.0,
            "tax": 0.0, "profit": 0.0, "profitability": 0.0,
            "penalty": 0.0, "additional_payment_sum": 0.0
        }
    ]

    return {
        'revenue_total': 0.0, 'sales_amount_total': 0.0, 'returns_amount_total': 0.0,
        'logistics_total': 0.0, 'net_costs_sum_total': 0.0, 'marginality_total': 0, 'commission_total': 0.0,
        'supplier_costs_total': 0.0, 'wb_costs_total': 0.0, 'tax_total': 0.0, 'profit_total': 0.0,
        'profitability_total': 0,
        'reports_by_week': json.dumps(reports_by_week),
        'brands_share_in_revenue_dict': json.dumps({"Название бренда": 100}, ensure_ascii=False),
        'stocks_share_in_revenue_dict': json.dumps({"Название категории": 100}, ensure_ascii=False),
        'category_share_in_revenue_dict': json.dumps({"Название склада": 100}, ensure_ascii=False)
    }


def get_demo_dashboard_by_barcode_data():
    today = datetime.date.today()

    totals = {
        'nm_id': 129494856, 'barcode': '2037015600756', 'ts_name': '37-41',
        'product_name': 'Название товара', 'revenue_total': 0.0,
        'sales_amount_total': 0.0, 'returns_amount_total': 0.0, 'logistics_total': 0, 'rom_total': 0,
        'total_payable': 0, 'net_costs_sum_total': 0, 'marginality_total': 0, 'commission_total': 0,
        'penalty_total': 0, 'additional_payment_sum_total': 0
    }

    report_by_week = [
        {
            "nm_id": 129494856, "barcode": "2037015600756", "ts_name": "37-41", "week_num": today.isocalendar()[1], "year": today.year,
            "product_name": "Название товара", "logistics": 0.0, "penalty": 0.0,
            "additional_payment_sum": 0.0, "revenue": 0.0, "net_costs_sum": 0.0, "marginality": 0.0,
            "sales_amount": 0.0, "returns_amount": 0.0, "commission": 0.0, "total_payable": 0.0,
            "rom": 0.0
        }
    ]

    products_by_barcodes = [
        {
            'nm_id': 129494856, 'barcode': '2038657935930', 'ts_name': '37-41',
            'image': None,
            'product_name': 'Название товара'
        }
    ]

    return {
        "totals": totals,
        "report_by_weeks": json.dumps(report_by_week, ensure_ascii=False),
        "products_by_barcodes": products_by_barcodes
    }
