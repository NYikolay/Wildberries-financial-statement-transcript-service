import json
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
                                                     test_robokassa_password_2, test_receipt_json)
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


def test_generate_payment_link(test_robokassa_login, test_robokassa_password_1, test_receipt_json):
    payment_link = generate_payment_link(
        test_robokassa_login,
        test_robokassa_password_1,
        Decimal('2200'),
        'Оплата подписки Commery.ru на срок 1 неделя',
        1,
        'admin@mail.ru',
        'ru',
        75,
        test_receipt_json,
        discount=50.00,
        duration=1,
        durationdesc='неделя',
        type='Start',
        user='admin@mail.ru'
    )

    assert payment_link.startswith('https://auth.robokassa.ru/Merchant/Index/')


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



