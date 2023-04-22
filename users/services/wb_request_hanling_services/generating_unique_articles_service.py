from typing import List


def get_unique_articles(sales: List[dict]) -> set:
    """
    Generating unique nm_ids
    :param sales: list of sales object
    :return: Dictionary containing dictionaries with unique nm_id and their brand_name from the sales parameter
    """

    nm_ids = set()
    for sale in sales:
        nm_id = sale.get('nm_id')
        if nm_id and nm_id != 99866376:
            nm_ids.add(nm_id)

    return nm_ids

