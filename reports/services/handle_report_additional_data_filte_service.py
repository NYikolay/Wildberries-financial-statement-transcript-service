from decimal import Decimal
from typing import List

import pandas as pd

from users.models import SaleReport


def create_reports_additional_data(file, current_api_key):
    report_data_df: pd.DataFrame = pd.read_excel(file)

    realizationreport_ids: List[int] = report_data_df['№ отчета'].unique().tolist()

    report_values_by_id: dict = report_data_df.set_index('№ отчета').to_dict('index')

    objs_to_update: list = []

    if all([isinstance(val, (int, float)) for val in realizationreport_ids]):
        current_user_reports = SaleReport.objects.filter(api_key=current_api_key).distinct(
            'realizationreport_id').in_bulk(realizationreport_ids, field_name='realizationreport_id')
    else:
        return False

    for realizationreport_id, report_object in current_user_reports.items():

        storage_cost = report_values_by_id.get(realizationreport_id).get('Стоимость хранения', Decimal('0.0'))
        cost_paid_acceptance = report_values_by_id.get(realizationreport_id).get(
            'Стоимость платной приемки',
            Decimal('0.0')
        )
        other_deductions = report_values_by_id.get(realizationreport_id).get('Прочие удержания', Decimal('0.0'))

        if all([isinstance(val, (int, float)) for val in [storage_cost, cost_paid_acceptance, other_deductions]]):
            report_object.storage_cost = storage_cost
            report_object.cost_paid_acceptance = cost_paid_acceptance
            report_object.other_deductions = other_deductions
            report_object.supplier_costs = report_object.supplier_costs or Decimal('0.0')

            objs_to_update.append(report_object)

    SaleReport.objects.bulk_update(
        objs_to_update,
        ['storage_cost', 'cost_paid_acceptance', 'other_deductions', 'supplier_costs']
    )

    return True
