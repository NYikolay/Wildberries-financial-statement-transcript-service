import decimal
from payments.services.generating_redirect_link import calculate_signature


def check_signature_result(
    order_number: int,
    received_sum: decimal,
    received_signature: hex,
    password: str,
    **kwargs
) -> bool:

    extra_params_for_signature = [f'Shp_{key}={kwargs[key]}' for key in sorted(kwargs)]

    signature = calculate_signature(
        received_sum,
        order_number,
        password,
        *extra_params_for_signature
    )
    if signature.lower() == received_signature.lower():
        return True
    return False
