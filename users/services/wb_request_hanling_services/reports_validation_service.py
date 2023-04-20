
def get_incorrect_reports_lst(sales: list) -> dict:
    """
    For each object in the sales parameter, it calls the validity check function.
    If the object is valid, move on to the next one.
    If the object does not pass validation, the values and unique identifier of the report
    are added to the invalid_reports dictionary
    :param sales: List of sales items received by request on Wildberries
    :return:
    """
    invalid_reports = {
        'realizationreport_ids': [],
        'incorrect_reports_data_list': []
    }

    for sale_obj in sales:
        sale_obj_validation_result: dict or bool = check_sale_obj_validation(sale_obj)

        if sale_obj_validation_result is True:
            continue

        if sale_obj_validation_result.get('realizationreport_id') not in invalid_reports.get('realizationreport_ids'):
            invalid_reports['realizationreport_ids'].append(sale_obj_validation_result.get('realizationreport_id'))
            invalid_reports['incorrect_reports_data_list'].append(
                sale_obj_validation_result.get('incorrect_report_data')
            )

    return invalid_reports


def check_sale_obj_validation(sale_obj: dict) -> True or dict:
    """
    Checks if certain object values are valid. Validation is performed under several conditions.
    1. None of the object values must be null
    2. If an object value is null, we check it for an additional conditions.
    :param sale_obj:
    :return: If the object passed the validation, we return True,
    otherwise we return the dictionary which includes some values of the object
    """
    delivery_rub: float = sale_obj.get('delivery_rub')
    office_name = 'Склад WB без названия' if not sale_obj.get('office_name') else sale_obj.get('office_name')

    sale_obj_values = [
        sale_obj.get('date_from'),
        sale_obj.get('realizationreport_id'),
        sale_obj.get('date_to'),
        sale_obj.get('create_dt'),
        sale_obj.get('gi_id'),
        sale_obj.get('subject_name'),
        sale_obj.get('nm_id'),
        sale_obj.get('brand_name'),
        sale_obj.get('ts_name'),
        sale_obj.get('barcode'),
        sale_obj.get('doc_type_name'),
        sale_obj.get('order_dt'),
        sale_obj.get('sale_dt'),
        sale_obj.get('quantity'),
        sale_obj.get('retail_price'),
        sale_obj.get('retail_price_withdisc_rub'),
        sale_obj.get('ppvz_for_pay'),
        sale_obj.get('penalty'),
        sale_obj.get('additional_payment'),
        sale_obj.get('site_country'),
        office_name,
        sale_obj.get('srid'),
        sale_obj.get('delivery_rub'),
        sale_obj.get('rid'),
        sale_obj.get('supplier_oper_name'),
        sale_obj.get('retail_amount')
    ]

    for value in sale_obj_values:
        additional_condition_1 = [
            delivery_rub is not None,
            delivery_rub > 0,
            sale_obj.get('supplier_oper_name') == "Логистика",
            sale_obj.get('realizationreport_id') is not None,
            sale_obj.get('date_from') is not None,
            sale_obj.get('date_to') is not None,
            sale_obj.get('create_dt') is not None,
            sale_obj.get('subject_name') is None,
            sale_obj.get('nm_id') is None,
            sale_obj.get('brand_name') is None,
            sale_obj.get('barcode') is not None,
            sale_obj.get('doc_type_name') == 'Продажа',
            sale_obj.get('quantity') == 0,
            sale_obj.get('retail_price_withdisc_rub') == 0,
            sale_obj.get('ppvz_for_pay') == 0
        ]
        additional_condition_2 = [
            sale_obj.get('realizationreport_id') is not None,
            sale_obj.get('date_from') is not None,
            sale_obj.get('date_to') is not None,
            sale_obj.get('create_dt') is not None,
            sale_obj.get('subject_name') is not None,
            sale_obj.get('nm_id') is not None,
            sale_obj.get('ts_name') is not None,
            sale_obj.get('barcode') is not None,
            sale_obj.get('doc_type_name') is not None,
            sale_obj.get('brand_name') is None,
            sale_obj.get('quantity') is not None,
            sale_obj.get('retail_amount') is not None,
            sale_obj.get('supplier_oper_name') is not None,
            sale_obj.get('retail_price_withdisc_rub') is not None,
            sale_obj.get('delivery_rub') is not None,
            sale_obj.get('ppvz_for_pay') is not None
        ]

        if value is None:
            if all(additional_condition_1) or all(additional_condition_2):
                return True

            return {
                'realizationreport_id': sale_obj.get('realizationreport_id'),
                'incorrect_report_data': {
                    'realizationreport_id': sale_obj.get('realizationreport_id'),
                    'date_from': sale_obj.get('date_from'),
                    'date_to': sale_obj.get('date_to')
                }
            }

    return True
