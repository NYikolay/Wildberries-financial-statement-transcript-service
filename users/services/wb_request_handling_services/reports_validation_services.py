import datetime
from typing import Set, List

import pandas as pd


def check_additional_conditions(row: pd.Series) -> bool:
    """
    The function is used to check the values in a particular row.

    additional_condition_* - a set of rules, if the values from the row meet each of these rules,
    then the row is valid, otherwise it is not

    Values of the row passed in parameters must satisfy at least one set of rules (additional_condition_* ),
    in this case the row is considered valid

    :param row: Pandas DataFrame row
    :return: True or False
    """
    delivery_rub = row.delivery_rub
    supplier_oper_name = row.supplier_oper_name
    realizationreport_id = row.realizationreport_id
    date_from = row.date_from
    date_to = row.date_to
    create_dt = row.create_dt
    subject_name = row.subject_name
    nm_id = row.nm_id
    brand_name = row.brand_name
    barcode = row.barcode
    doc_type_name = row.doc_type_name
    quantity = row.quantity
    retail_price_withdisc_rub = row.retail_price_withdisc_rub
    ppvz_for_pay = row.ppvz_for_pay
    ts_name = row.ts_name
    retail_amount = row.retail_amount
    delivery_amount = row.delivery_amount
    return_amount = row.return_amount
    product_discount_for_report = row.product_discount_for_report
    supplier_promo = row.supplier_promo
    order_dt = row.order_dt
    sale_dt = row.sale_dt
    rid = row.rid
    sticker_id = row.sticker_id
    site_country = row.site_country

    common_conditions: List[bool] = [
        pd.notna(realizationreport_id),
        pd.notna(date_from),
        pd.notna(date_to),
        pd.notna(create_dt),
        pd.notna(barcode)
    ]

    additional_condition_1: List[bool] = [
        *common_conditions,
        pd.notna(delivery_rub) and delivery_rub > 0,
        supplier_oper_name == "Логистика",
        pd.isna(subject_name),
        pd.isna(nm_id),
        pd.isna(brand_name),
        doc_type_name == 'Продажа',
        quantity == 0,
        retail_price_withdisc_rub == 0,
        ppvz_for_pay == 0
    ]

    additional_condition_2: List[bool] = [
        *common_conditions,
        pd.notna(subject_name),
        pd.notna(nm_id),
        pd.notna(ts_name),
        pd.isna(brand_name),
        pd.notna(quantity),
        pd.notna(retail_amount),
        pd.notna(supplier_oper_name),
        pd.notna(retail_price_withdisc_rub),
        pd.notna(delivery_rub),
        pd.notna(ppvz_for_pay)
    ]

    additional_condition_3: List[bool] = [
        supplier_oper_name in ('Перевыставление расходов по логистике', 'Возмещение издержек по перевозке'),
        pd.notna(barcode),
        pd.isna(order_dt),
        pd.isna(sale_dt),
        pd.isna(retail_price_withdisc_rub),
        pd.isna(delivery_amount),
        pd.isna(return_amount),
        pd.isna(delivery_rub),
        pd.isna(product_discount_for_report),
        pd.isna(supplier_promo),
        pd.isna(rid),
        pd.isna(sticker_id),
        pd.isna(site_country),
<<<<<<< HEAD
    ]
=======
        ]
>>>>>>> new_design

    if all(additional_condition_1) or all(additional_condition_2) or all(additional_condition_3):
        return True
    else:
        return False


def get_incorrect_reports(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    The function is responsible for generating incorrect reports, if any

    column_names - column names from data_frame param whose values should not be Null (NaN, None)

    incorrect_report_ids - the realizationreport_id values of incorrect sales, those that failed validation.
    It is necessary not to iterate over the same reports, but skip them if they are invalid

    result_list - a list containing tuples with incorrect report data, namely realizationreport_id, date_from, date_to

    result_df - the same as result list but converted in Pandas DataFrame

    The essence of the cycle "for" work:
    Iterates over each row of the DataFrame from the parameters.
    At each iteration, we check if at least one of the values in the current row is NaN or None (or in other words, Null),
    then we check if the report is already excluded from this sale (the current row).
    Then the check_additional_conditions function is called and the current row is passed to it.
    If the result of check_additional_conditions returns False, then we consider the report of this sale (current row)
    to be incorrect and add its values to incorrect_report_ids and result_list.
    If the current row is correct, we simply skip it

    :param data_frame: Pandas DataFrame with sales data
    :return: Pandas DataFrame with invalid (incorrect) reports
    """
    column_names = [
        'date_from', 'realizationreport_id', 'date_to', 'create_dt', 'gi_id', 'subject_name',
        'nm_id', 'brand_name', 'ts_name', 'barcode', 'doc_type_name', 'order_dt', 'sale_dt', 'quantity',
        'retail_price', 'retail_price_withdisc_rub', 'ppvz_for_pay', 'penalty', 'additional_payment',
        'site_country', 'delivery_rub', 'rid', 'supplier_oper_name', 'retail_amount'
    ]

    incorrect_report_ids: Set[int] = set()
    result_list: List[tuple] = []

    for row in data_frame.itertuples(index=False):
        if any([pd.isnull(getattr(row, column_name)) for column_name in column_names]):
            if row.realizationreport_id not in incorrect_report_ids:
                if not check_additional_conditions(row):
                    incorrect_report_ids.add(row.realizationreport_id)
                    result_list.append((row.realizationreport_id, row.date_from, row.date_to, row.create_dt))

    result_df = pd.DataFrame(result_list, columns=['realizationreport_id', 'date_from', 'date_to', 'create_dt'])

    return result_df
