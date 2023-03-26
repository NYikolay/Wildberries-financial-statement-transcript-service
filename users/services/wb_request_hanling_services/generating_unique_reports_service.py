from typing import List, Set


def get_unique_reports(sales: List[dict]) -> Set[int]:
    """
    Takes a list of sales objects as a parameter,
    and uses the set to select unique report numbers (realizationreport_id)
    It is used in functions such as get_wb_request_response and generate_reports_and_sales_objs
    :param sales: list of sales object
    :return: returns a set including all unique report numbers for the sales set
    """
    reports_data: Set[int] = set()
    for sale in sales:
        reports_data.add(sale.get('realizationreport_id'))
    return reports_data
