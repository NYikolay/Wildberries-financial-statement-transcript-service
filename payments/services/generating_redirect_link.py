import decimal
import hashlib
import json
from urllib import parse
import requests
from config.settings.base import ROBOKASSA_TARGET_URL, ROBOKASSA_TARGET_JSON_URL


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
    receipt,
    **kwargs
) -> str:

    final_extra_params_values = {f'Shp_{key}': kwargs[key] for key in sorted(kwargs)}
    extra_params_for_signature = [f'Shp_{key}={kwargs[key]}' for key in sorted(kwargs)]

    url_encoded_receipt = parse.quote(receipt)

    signature = calculate_signature(
        merchant_login,
        cost,
        inv_id,
        url_encoded_receipt,
        merchant_password_1,
        *extra_params_for_signature
    )

    data = {
        'MerchantLogin': merchant_login,
        'OutSum': cost,
        'InvId': inv_id,
        'Receipt': url_encoded_receipt,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test,
        'Email': customer_email,
        'Culture': culture,
        **final_extra_params_values
    }

    resp = requests.post(url=ROBOKASSA_TARGET_JSON_URL, data=data)
    resp_data = json.loads(resp.text)

    return f'{ROBOKASSA_TARGET_URL}{resp_data.get("invoiceID")}'

