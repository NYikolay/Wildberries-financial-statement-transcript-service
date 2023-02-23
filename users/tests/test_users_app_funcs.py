import json
from datetime import date
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.urls import reverse

from reports.views import DashboardView
from users.models import SaleObject, SaleReport, WBApiKey, User
from users.services.decrypt_api_key import get_decrypted_key
from users.services.encrypt_api_key import get_encrypted_key
from users.services.generate_last_report_date import get_last_report_date
from users.services.wb_request_hanling_services.generating_user_products_data import get_article_additional_data
from users.services.wb_request_hanling_services.request_data_handling import get_unique_articles, get_unique_reports
from users.tests.users_app_testing_data import test_sale_objs_data, test_articles_data


class TestUserAppFunctions(TestCase):

    def setUp(self) -> None:
        self.api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3'
        self.encrypted_api_key = get_encrypted_key(self.api_key)
        self.sale_objects = test_sale_objs_data
        self.decrypted_api_key = get_decrypted_key(self.encrypted_api_key)
        self.articles_data = test_articles_data

    def test_decrypt_api_key(self):
        self.assertFalse(self.decrypted_api_key == self.encrypted_api_key)

    def test_encrypt_api_key(self):
        self.assertEqual(self.api_key, self.decrypted_api_key)

    def test_generating_last_report_date(self):
        test_date = date.today() - relativedelta(months=3)
        test_first_date_of_month = test_date.replace(day=1)

        year = test_first_date_of_month.year - 1 \
            if test_first_date_of_month.isocalendar()[1] == 52 else test_first_date_of_month.year

        test_last_report_date = date.fromisocalendar(
            year,
            test_first_date_of_month.isocalendar()[1], 1).strftime('%Y-%m-%d')

        last_report_date = get_last_report_date()
        self.assertEqual(test_last_report_date, last_report_date)

    def test_generating_unique_articles(self):
        unique_articles = get_unique_articles(self.sale_objects)

        self.assertTrue(type(unique_articles) is list)
        self.assertTrue(len(unique_articles) > 0)
        self.assertTrue(type(unique_articles[0]) is dict)
        self.assertEqual(unique_articles, [{'brand': 'Hanes Store', 'nm_id': 129494856},
                                           {'brand': 'Hanes Store', 'nm_id': 129494851},
                                           {'brand': 'Hanes Store', 'nm_id': 129494822}])

    def test_generating_unique_reports(self):
        unique_reports = get_unique_reports(self.sale_objects)

        self.assertTrue(type(unique_reports) is set)
        self.assertTrue(len(unique_reports) > 0)
        self.assertEqual(unique_reports, {19279748, 19279741})

    def test_generating_user_products_data(self):
        article_obj_list = []

        for article_data in self.articles_data:
            get_article_additional_data(article_data.get('nm_id'), article_data.get('brand'), article_obj_list)

        self.assertEqual(len(article_obj_list), 5)
        self.assertTrue(type(article_obj_list[0]) is dict)
        self.assertEqual(article_obj_list[0].get('nm_id'), 94212294)
        self.assertEqual(article_obj_list[0].get('title'), 'Щетки стеклоочистителя')
        self.assertEqual(
            article_obj_list[0].get('img'),
            'https://basket-05.wb.ru//vol942/part94212/94212294/images/tm/1.jpg'
        )

