from contextlib import closing
from io import StringIO
from typing import List

from users.models import SaleObject

import pandas as pd

from users.services.wb_request_hanling_services.generating_objects_services import get_sale_object


def in_memory_csv(data: List[dict]):
    """
    Creates a csv file to store in memory.
    :param data: Pandas DataFrame with SaleObject data
    :return:
    """
    mem_csv = StringIO()

    dtypes: List[str] = [
        'nm_id', 'rid', 'rrd_id', 'product',
        'shk_id', 'ppvz_supplier_id',
        'delivery_amount', 'return_amount', 'ppvz_office_id'
    ]

    df: pd.DataFrame = pd.DataFrame(data)

    # Changing type for columns with name in dtypes to integer
    for column_name in dtypes:
        df[column_name] = df[column_name].astype('Int64')

    df.to_csv(mem_csv, index=False)

    mem_csv.seek(0)
    return mem_csv


def create_sale_objects(
        current_user,
        current_api_key,
        sales_data_frame: pd.DataFrame,
        existing_reports_ids: List[int],
        incorrect_reports_ids: List[int],
        existing_products: dict
) -> dict:
    """
    The function is responsible for creating SaleObjects in the database using COPY in PostgreSQL

    The first thing is to iterate over the sales_data_frame passed in the parameters of
    Pandas DataFrame and create dictionaries with sales data, and for each row there is a check that the
    realizationreport_id of the current sale (row) should not be included in
    existing_reports_ids and incorrect_reports_ids

    If after generating sales_to_create there is no value in the list, we return a message to the user
    that there are no reports

    :param current_user:  User object, authorized user
    :param current_api_key: WBApiKey object, active api key
    :param sales_data_frame: Pandas DataFrame, consisting of sales data from the Wildberries API
    :param existing_reports_ids: A list consisting of the objects already created in the SaleReport database
    :param incorrect_reports_ids: A list consisting of the realizationreport_id of invalid reports that failed validation
    :param existing_products: Dictionary consisting of ClientUniqueProduct objects as values
    :return: Dictionary with the status of the function
    """

    sales_to_create: List[dict] = [
        get_sale_object(current_user, row, current_api_key, existing_products)
        for row in sales_data_frame.itertuples()
        if row.realizationreport_id not in existing_reports_ids
        and row.realizationreport_id not in incorrect_reports_ids
    ]

    if not sales_to_create:
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }

    mem_csv = in_memory_csv(sales_to_create)
    with closing(mem_csv) as csv_io:
        SaleObject.objects.from_csv(csv_io, drop_indexes=False, drop_constraints=False)

    return {
        'status': True
    }
