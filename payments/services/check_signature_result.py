import decimal
from payments.services.generating_redirect_link import calculate_signature


def check_signature_result(
    order_number: int,
    received_sum: decimal,
    received_signature: hex,
    password: str,
    shp_discount: decimal,
    shp_duration: int,
    shp_durationdesc: str,
    shp_type: str,
    shp_user: str
) -> bool:

    extra_params_for_signature = [
        f'Shp_discount={shp_discount}',
        f'Shp_duration={shp_duration}',
        f'Shp_durationdesc={shp_durationdesc}',
        f'Shp_type={shp_type}',
        f'Shp_user={shp_user}'
    ]

    signature = calculate_signature(
        received_sum,
        order_number,
        password,
        *extra_params_for_signature
    )
    if signature.lower() == received_signature.lower():
        return True
    return False
