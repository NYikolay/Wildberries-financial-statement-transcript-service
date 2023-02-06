from users.models import User, ClientUniqueProduct


def handle_unique_articles(article_values: dict, api_key):
    return ClientUniqueProduct(
        api_key=api_key,
        nm_id=article_values.get('nm_id', 0),
        brand=article_values.get('brand'),
        image=article_values.get('img', 'https://None.ru'),
        product_name=article_values.get('title', 'None')
    )
