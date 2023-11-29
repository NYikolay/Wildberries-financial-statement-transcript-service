import pandas as pd


def get_barcodes_detail_dataframe(report_by_barcodes):
    report_by_barcodes_df = pd.DataFrame(report_by_barcodes)
    report_by_barcodes_df.drop(
        columns=[
            'coefficient_xyz', 'std_revenue', 'increasing_proportion',
            'group_abc', 'mean_revenue', 'coefficient_xyz', 'group', 'share_in_number', 'final_group'
        ],
        axis=1,
        inplace=True
    )

    report_by_barcodes_df.rename(
        columns={
            'nm_id': ' Артикул',
            'barcode': ' Баркод',
            'ts_name': 'Размер',
            'image': 'Картинка',
            'product_name': 'Наименование товара',
            'logistics': 'Логистика',
            'penalty_sum': 'Штрафы',
            'additional_payment_sum': 'Доплаты',
            'revenue': 'Выручка',
            'share_in_revenue': 'Доля в выручке',
            'product_marginality': 'Маржинальность',
            'sales_amount': 'Продажи',
            'returns_amount': 'Возвраты',
            'commission': 'Комиссия',
            'net_costs_sum': 'Себестоиомсть продаж',
            'total_payable': 'Валовая прибыль',
            'rom': 'ROM',
        }, inplace=True
    )

    return report_by_barcodes_df


def get_penalties_dataframe(penalties_data):
    penalties_df = pd.DataFrame(penalties_data)

    penalties_df.rename(
        columns={
            "bonus_type_name": "Обоснование штрафов и доплат",
            "nm_id": "Артикул",
            "realizationreport_id": "Номер отчёта",
            "week_num": "Неделя",
            "total_sum": "Сумма",
            "date_from": "Дата начала отчетного периода",
            "date_to": "Дата конца отчетного периода"
        },
        inplace=True
    )

    return penalties_df
