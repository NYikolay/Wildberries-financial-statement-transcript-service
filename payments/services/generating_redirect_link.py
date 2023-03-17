import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse

import requests

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
    customer_email,
    culture,
    number,
    **kwargs
) -> str:

    sorted_extra_params = sorted([(f'Shp_{key}', value) for key, value in kwargs.items()])
    final_extra_params_values = {param_name: param_value for param_name, param_value in sorted_extra_params}
    extra_params_for_signature = [f'{param_name}={param_value}' for param_name, param_value in sorted_extra_params]

    signature = calculate_signature(
        merchant_login,
        cost,
        number,
        merchant_password_1,
        *extra_params_for_signature
    )

    data = {
        'MerchantLogin': merchant_login,
        'OutSum': cost,
        'InvId': number,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test,
        'Email': customer_email,
        'Culture': culture,
        **final_extra_params_values
    }

    return f'{ROBOKASSA_TARGET_URL}?{parse.urlencode(data)}'

