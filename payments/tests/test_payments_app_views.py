import pytest

from django.urls import reverse
from django.contrib.messages import get_messages

from config.settings.base import ROBOKASSA_TARGET_URL
from payments.models import SubscriptionTypes, SuccessPaymentNotification, FailPaymentNotification
from payments.tests.payments_pytest_fixtures import (
    test_redirect_to_robokassa_view_data, create_order, create_success_payment_notification
)
from users.models import UserSubscription, Order
from users.tests.users_pytest_fixtures import (create_user,
                                               create_subscription_types,
                                               test_password,
                                               test_subscriptions_data)


@pytest.mark.django_db
def test_redirect_to_robokassa_view(client, create_user, test_redirect_to_robokassa_view_data):
    """
    The test checks if the RedirectToRobokassaView view is valid when the data is transferred correctly.
    :param client:
    :param create_user: Fixture to create a test user in database
    :param test_redirect_to_robokassa_view_data: Fixture that contains
    test data to send post request (which will go into RoboKassaForm)
    """
    user = create_user()
    url = reverse('payments:generate_robokassa_redirection')
    data = test_redirect_to_robokassa_view_data
    client.force_login(user)
    response = client.post(url, data)
    messages = list(get_messages(response.wsgi_request))

    assert response.status_code == 302
    assert response['Location'].startswith(ROBOKASSA_TARGET_URL)
    assert user.orders.count() == 1
    assert len(messages) == 0


@pytest.mark.django_db
def test_fail_form_errors_redirect_to_robokassa_view(client, create_user):
    """
    The test checks if the RedirectToRobokassaView view is valid when the post data is not transferred correctly.
    In other words, there is a RoboKassaForm validation error in the data sent through the Post request
    :param client:
    :param create_user: Fixture to create a test user in database
    """
    user = create_user()
    url = reverse('payments:generate_robokassa_redirection')
    data = {
        "fail_form": "fail"
    }

    client.force_login(user)
    response = client.post(url, data)
    messages = list(get_messages(response.wsgi_request))

    assert response.status_code == 302
    assert response['Location'] == reverse('users:profile')
    assert user.orders.count() == 0
    assert len(messages) == 1


@pytest.mark.django_db
def test_fail_not_authorized_redirect_to_robokassa_view(client, create_user, test_redirect_to_robokassa_view_data):
    """
    The test checks the behavior of the RedirectToRobokassaView view
    when an unauthorized user tries to make a post request
    :param client:
    :param create_user: Fixture to create a test user in database
    :param test_redirect_to_robokassa_view_data: Fixture that contains
    test data to send post request (which will go into RoboKassaForm)
    """
    user = create_user()
    url = reverse('payments:generate_robokassa_redirection')
    data = test_redirect_to_robokassa_view_data
    response = client.post(url, data)
    messages = list(get_messages(response.wsgi_request))

    assert response.status_code == 302
    assert response['Location'].startswith(reverse('users:login'))
    assert user.orders.count() == 0
    assert len(messages) == 0


@pytest.mark.django_db
def test_receive_result_view(client, create_order):
    """
    The test checks if the data of ReceiveResultView view is processed correctly with valid data.
    SignatureValue result of calculate_signature function (payments.services.generating_redirect_link),
    done manually (InvId == 2)
    :param client:
    :param create_order: Fixture to create an Order object
    :return:
    """
    url = reverse('payments:payment_result')
    order = create_order(paid_sum=4200, status="proceed")

    data = {
        "OutSum": 4200,
        "InvId": order.id,
        "SignatureValue": 'f7665e26a641933be5d7936a4152afc7',
        "Shp_discount": 0,
        "Shp_duration": 1,
        "Shp_durationdesc": "Месяц",
        "Shp_type": SubscriptionTypes.START,
        "Shp_user": "commery_123test@mail.ru"
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert SuccessPaymentNotification.objects.filter(out_sum=4200).exists()
    assert Order.objects.get(id=order.id).status == 'paid'
    assert response.content == b'OK2'


@pytest.mark.django_db
def test_receive_result_view_fail_form(client):
    """
    The test checks if the data of ReceiveResultView view is processed correctly with invalid data.
    In other words, there is a ResultURLForm validation error in the data sent through the Post request
    :param client:
    :return:
    """
    url = reverse('payments:payment_result')

    data = {}

    response = client.post(url, data)

    assert response.status_code == 200
    assert UserSubscription.objects.count() == 0
    assert response.content == b'error: bad signature'


@pytest.mark.django_db
def test_receive_result_view_fail_signature(client, create_order):
    """
    The test checks if the data of ReceiveResultView view is processed correctly with invalid SIGNATURE.
    In other words, there is a ResultURLForm validation error in the signature
    sent through the Post request (method clean).
    :param client:
    :param create_order: Fixture to create an Order object
    :return:
    """
    url = reverse('payments:payment_result')

    order = create_order(paid_sum=4200, status="proceed")

    data = {
        "OutSum": 4200,
        "InvId": order.id,
        "SignatureValue": 'asdasd3123qwdwqe<script>alert("213123")</script>',
        "Shp_discount": 0,
        "Shp_duration": 1,
        "Shp_durationdesc": "Месяц",
        "Shp_type": SubscriptionTypes.START,
        "Shp_user": "commery_123test@mail.ru"
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert UserSubscription.objects.count() == 0
    assert response.content == b'error: bad signature'


@pytest.mark.django_db
def test_success_payment_view(
        client,
        create_user,
        create_order,
        create_success_payment_notification,
        create_subscription_types
):
    """
    The test verifies that the SuccessPaymentView view works correctly with valid data in the post request.
    It also checks if a subscription is created for a specific user
    :param client:
    :param create_user: Fixture to create a test user in database
    :param create_order: Fixture to create an Order object
    :param create_success_payment_notification: Fixture to create an SuccessPaymentNotification object
    :param create_subscription_types: Fixture to create an SubscriptionType objects
    :return:
    """
    url = reverse('payments:success_payment')
    user = create_user()
    order = create_order(paid_sum=4200, status="proceed")
    notification = create_success_payment_notification(inv_id=order.id, out_sum=4200)
    sub_types = create_subscription_types
    data = {
        "OutSum": 4200,
        "InvId": order.id,
        "SignatureValue": 'bc01422979195c701f0019a6b097c703',
        "Shp_discount": 0,
        "Shp_duration": 1,
        "Shp_durationdesc": "Месяц",
        "Shp_type": SubscriptionTypes.START,
        "Shp_user": user.email
    }

    response = client.post(url, data)
    messages = list(get_messages(response.wsgi_request))
    assert response.status_code == 302
    assert UserSubscription.objects.filter(user=user).exists()
    assert response['Location'] == reverse('users:profile')
    assert messages[0].message == 'Оплата прошла успешно'


@pytest.mark.django_db
def test_success_payment_view_fail_form(
        client,
):
    """
    The test checks if the SuccessPaymentView view works correctly with invalid data in the post request.
    It also checks that no subscription should be created for a specific user.
    :param client:
    """
    url = reverse('payments:success_payment')
    data = {}

    response = client.post(url, data)
    messages = list(get_messages(response.wsgi_request))
    assert response.status_code == 302
    assert UserSubscription.objects.count() == 0
    assert response['Location'] == reverse('users:profile')
    assert messages[0].message == 'Оплата не удалась. Если средства были списаны, ' \
                                  'пожалуйста, свяжитесь со службой поддержки'


@pytest.mark.django_db
def test_success_payment_view_fail_signature(
        client,
        create_user,
        create_order,
        create_success_payment_notification,
        create_subscription_types
):
    """
    The test verifies that the SuccessPaymentView view works correctly with an BAD SIGNATURE in the post request.
    It also checks that no subscription should be created for a specific user
    :param client:
    :param create_user: Fixture to create a test user in database
    :param create_order: Fixture to create an Order object
    :param create_success_payment_notification: Fixture to create an SuccessPaymentNotification object
    :param create_subscription_types: Fixture to create an SubscriptionType objects
    :return:
    """
    url = reverse('payments:success_payment')
    user = create_user()
    order = create_order(paid_sum=4200, status="proceed")
    notification = create_success_payment_notification(inv_id=order.id, out_sum=4200)
    sub_types = create_subscription_types
    data = {
        "OutSum": 4200,
        "InvId": order.id,
        "SignatureValue": 'asdasdsadklkj123',
        "Shp_discount": 0,
        "Shp_duration": 1,
        "Shp_durationdesc": "Месяц",
        "Shp_type": SubscriptionTypes.START,
        "Shp_user": user.email
    }

    response = client.post(url, data)

    messages = list(get_messages(response.wsgi_request))
    assert response.status_code == 302
    assert UserSubscription.objects.count() == 0
    assert response['Location'] == reverse('users:profile')
    assert messages[0].message == 'Оплата не удалась. Если средства были списаны, ' \
                                  'пожалуйста, свяжитесь со службой поддержки'


@pytest.mark.django_db
def test_fail_payment_view(client, create_order):
    """
    The test verifies that the FailPaymentView view works correctly with valid data in the post request.
    It also checks that no FailPaymentNotification should be created and Order status changed to FAIL
    :param client:
    :param create_order:
    :return:
    """
    url = reverse('payments:fail_payment')
    order = create_order(paid_sum=4200, status="proceed")

    data = {
        "OutSum": 4200,
        "InvId": order.id,
    }

    response = client.post(url, data)
    messages = list(get_messages(response.wsgi_request))
    assert response['Location'] == reverse('users:profile')
    assert FailPaymentNotification.objects.filter(inv_id=order.id).exists()
    assert Order.objects.get(id=order.id).status == 'fail'
    assert messages[0].message == 'Оплата была отменена'


@pytest.mark.django_db
def test_fail_payment_view_fail_form(client):
    """
    The test verifies that the FailPaymentView view works correctly with invalid data in the post request.
    It also checks that no FailPaymentNotification should be created and Order status changed to FAIL
    :param client:
    :return:
    """
    url = reverse('payments:fail_payment')

    data = {}

    response = client.post(url, data)
    messages = list(get_messages(response.wsgi_request))
    assert response['Location'] == reverse('users:profile')
    assert FailPaymentNotification.objects.count() == 0
    assert messages[0].message == 'Оплата была отменена'

