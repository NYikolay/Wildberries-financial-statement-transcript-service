from decimal import Decimal
from datetime import datetime, time

import pytest
from dateutil.relativedelta import relativedelta

from payments.models import SubscriptionTypes
from payments.services.create_user_subscription_service import create_user_subscription
from payments.services.generating_redirect_link import calculate_signature, generate_payment_link
from payments.services.check_signature_result import check_signature_result
from payments.services.generating_subscribed_to_date import get_subscribed_to_date
from payments.tests.payments_pytest_fixtures import (test_robokassa_password_1,
                                                     test_robokassa_shp_params,
                                                     test_robokassa_login,
                                                     test_robokassa_password_2)
from users.tests.users_pytest_fixtures import (create_user,
                                               create_subscription_types,
                                               test_password,
                                               test_subscriptions_data)


def test_calculate_signature(test_robokassa_login, test_robokassa_password_1, test_robokassa_shp_params):
    signature = calculate_signature(
        test_robokassa_login, Decimal('4400'), 1,
        test_robokassa_password_1, *test_robokassa_shp_params
    )

    assert signature == '5b680f1bcd1b8c53388d32d99f066948'


def test_generate_payment_link(test_robokassa_login, test_robokassa_password_1):
    payment_link = generate_payment_link(
        test_robokassa_login,
        test_robokassa_password_1,
        Decimal('2200'),
        'Оплата подписки Commery.ru на срок 1 неделя',
        1,
        'admin@mail.ru',
        'ru',
        75,
        discount=50.00,
        duration=1,
        durationdesc='неделя',
        type='Start',
        user='admin@mail.ru'
    )

    assert payment_link == 'https://auth.robokassa.ru/Merchant/Index.aspx?' \
                           'MerchantLogin=com123op&' \
                           'OutSum=2200&' \
                           'InvId=75&' \
                           'Description=%D0%9E%D0%BF%D0%BB%D0%B0%D1%82%D0%B0+' \
                           '%D0%BF%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%BA%D0%B8+Commery.ru+%D0%BD%D0%B0+' \
                           '%D1%81%D1%80%D0%BE%D0%BA+1+%D0%BD%D0%B5%D0%B4%D0%B5%D0%BB%D1%8F&' \
                           'SignatureValue=48ba8ec000fe71b933f221095c6e4814&' \
                           'IsTest=1&Email=admin%40mail.ru&' \
                           'Culture=ru&Shp_discount=50.0&' \
                           'Shp_duration=1&Shp_durationdesc=%D0%BD%D0%B5%D0%B4%D0%B5%D0%BB%D1%8F&' \
                           'Shp_type=Start&Shp_user=admin%40mail.ru'


def test_success_check_signature_result(
        test_robokassa_login,
        test_robokassa_password_2,
        test_robokassa_shp_params
):
    signature = calculate_signature(Decimal('4400'), 1, test_robokassa_password_2, *test_robokassa_shp_params)
    signature_result = check_signature_result(
        1, Decimal('4400'), signature, test_robokassa_password_2,
        discount=0, duration=1, durationdesc='Неделя', type='TEST', user='admin@mail.ru'
    )

    assert signature_result


def test_fail_check_signature_result(
        test_robokassa_login,
        test_robokassa_password_1,
        test_robokassa_password_2,
        test_robokassa_shp_params
):
    signature = calculate_signature(Decimal('4400'), 1, test_robokassa_password_1, *test_robokassa_shp_params)
    signature_result = check_signature_result(
        1, Decimal('4400'), signature, test_robokassa_password_2,
        discount=0, duration=1, durationdesc='Неделя', type='TEST', user='admin@mail.ru'
    )

    assert signature_result is False


def test_get_subscribed_to_date():
    current_date = datetime.now()
    expected_subscribed_to_1 = datetime.combine((current_date + relativedelta(weeks=1)), time.max)
    subscribed_to_1 = get_subscribed_to_date(1, 'Неделя')

    expected_subscribed_to_2 = datetime.combine((current_date + relativedelta(months=1)), time.max)
    subscribed_to_2 = get_subscribed_to_date(1, 'Месяц')

    assert subscribed_to_1 == expected_subscribed_to_1
    assert subscribed_to_2 == expected_subscribed_to_2


@pytest.mark.django_db
def test_create_user_subscription(create_user, create_subscription_types):
    user = create_user()
    subscription_types = create_subscription_types

    create_user_subscription(
        user,
        SubscriptionTypes.TEST,
        Decimal('4200'),
        1,
        'Неделя',
        Decimal('0')
    )

    assert user.subscriptions.count() == 1



