from typing import List


def get_unique_articles(sales: List[dict]) -> List[dict]:
    """
    Forming a list with article data, namely brand_name and nm_id.
    Since Wildberries can give the object sales from the list of sales - nm_id which has both brand_name == None
    and brand_name != None (that is, a string with the name of the brand) used to check for subsequent sales
    and exclude the value with brand_name == None if the same nm_id occurs brand_name != None. Example:
    articles_data = [
    {'nm_id': 1, 'brand': 'Zara'},
    {'nm_id': 1, 'brand': None},
    {'nm_id': 2, 'brand': None},
    {'nm_id': 3, 'brand': 'H&M'},
    {'nm_id': 3, 'brand': None}]
    On this basis the following dictionaries are deleted:
    {'nm_id': 1, 'brand': None} and {'nm_id': 3, 'brand': None}
    and the final new_articles_data will look like
    [{'nm_id': 1, 'brand': 'Zara'}, {'nm_id': 2, 'brand': None}, {'nm_id': 3, 'brand': 'H&M'}]
    :param sales: list of sales object
    :return: Dictionary containing dictionaries with unique nm_id and their brand_name from the sales parameter
    """

    articles_data: List[dict] = []
    nm_ids = set()
    for sale in sales:
        conditions = [
            sale.get('supplier_oper_name').lower() != 'логистика',
            sale.get('supplier_oper_name').lower() != 'логистика сторно'
        ]

        nm_id = sale.get('nm_id')
        article_data = {'nm_id': nm_id, 'brand': sale.get('brand_name')}

        if all(conditions) and nm_id and article_data not in articles_data:
            articles_data.append({'nm_id': nm_id, 'brand': sale.get('brand_name')})
            nm_ids.add(nm_id)

    print(articles_data)
    # Create a dictionary where the keys are `nm_id` values and the values are sets of corresponding non-null brands.
    grouped_data = {}
    for article in articles_data:
        nm_id, brand = article['nm_id'], article['brand']
        if nm_id not in grouped_data and brand:
            grouped_data[nm_id] = {brand}
        elif brand:
            grouped_data[nm_id].add(brand)

    # Remove dictionaries with `brand == None` if there exists a non-null brand for the
    new_articles_data = []
    for article in articles_data:
        nm_id, brand = article['nm_id'], article['brand']
        if brand or nm_id not in grouped_data or not grouped_data[nm_id]:
            new_articles_data.append(article)
        elif not brand:
            grouped_data[nm_id].discard(None)

    return new_articles_data

