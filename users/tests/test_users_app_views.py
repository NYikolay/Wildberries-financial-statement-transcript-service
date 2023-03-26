import uuid

import pytest
from django.urls import reverse

from users.models import User
from users.tests.pytest_fixtures import test_password, create_user


@pytest.mark.django_db
def test_success_register_page_view(client):
    url = reverse('users:register')

    data = {
        "email": "commery_123test@mail.ru",
        "is_accepted_terms_of_offer": True,
        "password1": "12345678test",
        "password2": "12345678test"
    }
    response = client.post(url, data)
    session = client.session

    user = User.objects.get(
        email="commery_123test@mail.ru"
    )

    assert session['new_email'] == user.email
    assert session['email_message_timestamp']
    assert user.is_active is False
    assert user.email == "commery_123test@mail.ru"
    assert response.status_code == 302


# @pytest.mark.django_db
# def test_success_login_view(client, create_user, test_password):
#     url = reverse('users:login')
#     user = create_user()
#
#     data = {
#         "email": user.email,
#         "password": test_password
#     }
#
#     response = client.post(url, data)
#     assert response.status_code == 302
#
#
# @pytest.mark.django_db
# def test_fail_login_view(client, create_user, test_password):
#     url = reverse('users:login')
#     create_user()
#
#     data = {
#         "email": '123123',
#         "password": test_password
#     }
#
#     response = client.post(url, data)
#     assert response.status_code == 200
#     assert "Введён неверный пароль или почта." in response.content
