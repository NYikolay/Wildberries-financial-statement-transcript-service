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
            'logistic_sum': 'Логистика',
            'penalty_sum': 'Штрафы',
            'additional_payment_sum': 'Доплаты',
            'revenue_by_article': 'Выручка',
            'share_in_revenue': 'Доля в выручке',
            'product_marginality': 'Маржинальность',
            'sales_quantity': 'Продажи',
            'returns_quantity': 'Возвраты',
            'commission': 'Комиссия',
            'total_payable': 'Итого к оплате',
            'rom': 'ROM'
        }, inplace=True
    )

    return report_by_barcodes_df
