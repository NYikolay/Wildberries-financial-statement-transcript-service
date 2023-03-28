import decimal
import hashlib
from urllib import parse

from config.settings.base import ROBOKASSA_TARGET_URL


def calculate_signature(*args) -> str:
    """Create signature MD5.
    """
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def generate_payment_link(
    merchant_login: str,
    merchant_password_1: str,
    cost: decimal,
    description: str,
    is_test: int,
    customer_email: str,
    culture: str,
    inv_id: int,
    **kwargs
) -> str:

    final_extra_params_values = {f'Shp_{key}': kwargs[key] for key in sorted(kwargs)}
    extra_params_for_signature = [f'Shp_{key}={kwargs[key]}' for key in sorted(kwargs)]

    signature = calculate_signature(
        merchant_login,
        cost,
        inv_id,
        merchant_password_1,
        *extra_params_for_signature
    )

    data = {
        'MerchantLogin': merchant_login,
        'OutSum': cost,
        'InvId': inv_id,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test,
        'Email': customer_email,
        'Culture': culture,
        **final_extra_params_values
    }

    return f'{ROBOKASSA_TARGET_URL}?{parse.urlencode(data)}'

