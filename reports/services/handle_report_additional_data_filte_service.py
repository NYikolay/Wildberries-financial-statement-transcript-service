from decimal import Decimal
from typing import List
import pandas as pd

from users.models import SaleReport


def create_reports_additional_data(file, current_api_key):
    report_data_df = pd.read_excel(file)

    realizationreport_ids: List[int] = report_data_df['№ отчета'].unique().tolist()

    report_values_by_id: dict = report_data_df.set_index('№ отчета').to_dict('index')

    objs_to_update = []

    current_user_reports = SaleReport.objects.filter(api_key=current_api_key).distinct(
        'realizationreport_id').in_bulk(realizationreport_ids, field_name='realizationreport_id')

    for key, report_object in current_user_reports.items():
        report_object.storage_cost = report_values_by_id.get(key).get('Стоимость хранения', Decimal('0.0'))
        report_object.cost_paid_acceptance = report_values_by_id.get(key).get(
            'Стоимость платной приемки',
            Decimal('0.0')
        )
        report_object.other_deductions = report_values_by_id.get(key).get('Прочие удержания', Decimal('0.0'))
        report_object.supplier_costs = Decimal('0.0')

        objs_to_update.append(report_object)

    SaleReport.objects.bulk_update(
        objs_to_update,
        ['storage_cost', 'cost_paid_acceptance', 'other_deductions', 'supplier_costs']
    )
