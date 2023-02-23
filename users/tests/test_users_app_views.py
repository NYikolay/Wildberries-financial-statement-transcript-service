import json

from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.urls import reverse

from reports.views import DashboardView
from users.models import SaleObject, SaleReport, WBApiKey, User


class TestUserAppViews(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email='test_user@mail.ru',
            is_accepted_terms_of_offer=True
        )

    def test_user_email(self):
        self.assertEqual(self.user.email, 'test_user@mail.ru')
