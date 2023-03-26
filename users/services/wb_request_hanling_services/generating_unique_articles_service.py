
from typing import List


def get_unique_articles(sales: List[dict]) -> List[dict]:
    articles_data: List[dict] = []
    for sale in sales:
        articles_nm_ids: List[int] = [i.get('nm_id') for i in articles_data]
        if sale.get('nm_id') not in articles_nm_ids and sale.get('nm_id'):
            articles_data.append(
                {
                    'nm_id': sale.get('nm_id'),
                    'brand': sale.get('brand_name')
                }
            )
    return articles_data
