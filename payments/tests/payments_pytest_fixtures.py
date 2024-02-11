import json

import pytest

from payments.models import SubscriptionTypes, SuccessPaymentNotification
from users.models import Order


@pytest.fixture
def test_robokassa_login():
    return 'com123op'


@pytest.fixture
def test_receipt_json():
    receipt_json = {
        "items": [
            {
                "name": "Оплата информационно-аналитических и консалтинговых услуг на "
                        "портале сервиса за 1 месяц",
                "quantity": 1,
                "sum": 4200,
                "payment_method": "full_payment",
                "tax": "none"
            }
        ]
    }
    return json.dumps(receipt_json, ensure_ascii=False)


@pytest.fixture
def test_robokassa_password_1():
    return 'm5LQps4gJmIx9KXuI18Y'


@pytest.fixture
def test_robokassa_password_2():
    return 'k5LUps4gYmIx9LXuJ18N'


@pytest.fixture
def test_robokassa_shp_params():
    return [
        'Shp_discount=0',
        'Shp_duration=1',
        'Shp_durationdesc=Неделя',
        'Shp_type=TEST',
        'Shp_user=admin@mail.ru'
    ]


@pytest.fixture
def test_redirect_to_robokassa_view_data(test_receipt_json):

    return {
        "OutSum": 4200,
        "Description": "Подписка Commery на 1 месяц",
        "CustomerEmail": "admin@mail.ru",
        "Receipt": test_receipt_json,
        "UserEmail": "admin@mail.ru",
        "SubscriptionType": SubscriptionTypes.START,
        "Culture": "ru",
        "Discount": 0,
        "Duration": 1,
        "DurationDescription": "Месяц"
    }


@pytest.fixture
def create_order(db):
    def make_order(**kwargs):
        return Order.objects.create(**kwargs)

    return make_order


@pytest.fixture
def create_success_payment_notification(db):
    def make_success_payment_notification(**kwargs):
        return SuccessPaymentNotification.objects.create(**kwargs)

    return make_success_payment_notification

