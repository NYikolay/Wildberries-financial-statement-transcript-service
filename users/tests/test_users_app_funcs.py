from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone

from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.urls import reverse

from reports.views import DashboardView
from users.models import SaleObject, SaleReport, WBApiKey, User, IncorrectReport, ClientUniqueProduct
from users.services.decrypt_api_key import get_decrypted_key
from users.services.encrypt_api_key import get_encrypted_key
from users.services.generate_last_report_date import get_last_report_date
from users.services.wb_request_hanling_services.generating_incorrect_reports import generate_incorrect_reports
from users.services.wb_request_hanling_services.generating_user_products_data import handle_article_additional_data
from users.services.wb_request_hanling_services.generating_user_products_objs import generate_user_products
from users.services.wb_request_hanling_services.generating_user_reports import generate_reports
from users.services.wb_request_hanling_services.reports_validation import check_sale_obj_validation, \
    get_incorrect_reports_lst
from users.services.wb_request_hanling_services.generating_unique_reports import get_unique_reports
from users.services.wb_request_hanling_services.request_data_handling import get_unique_articles
from users.tests.users_app_testing_data import test_sale_objs_data, test_articles_data, test_user_data, \
    test_incorrect_reports_data, test_invalid_objs_data


class TestUserAppFunctions(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email=test_user_data.get('email'),
            is_accepted_terms_of_offer=True,
            password=test_user_data.get('password')
        )
        self.api_key_obj = WBApiKey.objects.create(
            api_key=get_encrypted_key('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3'),
            name='Test Company',
            user=self.user,
            is_current=True,
            is_wb_data_loaded=True,
            is_products_loaded=True,
        )
        self.sale_objects = test_sale_objs_data
        self.articles_data = test_articles_data
        self.invalid_sale_objects = test_invalid_objs_data

        sale_objs = []

        for sale in self.sale_objects:
            wb_office_name = sale.get('office_name', None)
            office_name = 'Склад WB без названия' if wb_office_name is None else wb_office_name
            sale_objs.append(SaleObject(
                owner=self.user,
                api_key=self.api_key_obj,
                week_num=
                datetime.strptime(sale.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').
                replace(tzinfo=timezone.utc).isocalendar()[1],
                year=datetime.strptime(sale.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').
                replace(tzinfo=timezone.utc).year,
                month_num=datetime.strptime(sale.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').
                replace(tzinfo=timezone.utc).month,
                realizationreport_id=sale.get('realizationreport_id'),
                date_from=datetime.strptime(sale.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').replace(
                    tzinfo=timezone.utc),
                date_to=datetime.strptime(sale.get('date_to'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
                create_dt=datetime.strptime(sale.get('create_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(
                    tzinfo=timezone.utc),
                gi_id=sale.get('gi_id'),
                subject_name=sale.get('subject_name'),
                nm_id=sale.get('nm_id'),
                brand_name=sale.get('brand_name'),
                sa_name=sale.get('sa_name'),
                ts_name=sale.get('ts_name'),
                barcode=sale.get('barcode'),
                doc_type_name=sale.get('doc_type_name'),
                order_dt=datetime.strptime(sale.get('order_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
                sale_dt=datetime.strptime(sale.get('sale_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
                quantity=sale.get('quantity'),
                retail_price=sale.get('retail_price'),
                retail_price_withdisc_rub=sale.get('retail_price_withdisc_rub'),
                ppvz_for_pay=sale.get('ppvz_for_pay'),
                penalty=sale.get('penalty'),
                additional_payment=sale.get('additional_payment'),
                site_country=sale.get('site_country'),
                office_name=office_name,
                srid=sale.get('srid'),
                delivery_rub=sale.get('delivery_rub'),
                rid=sale.get('rid'),
                supplier_oper_name=sale.get('supplier_oper_name'),
                ))

        SaleObject.objects.bulk_create(sale_objs)

    def test_decrypt_api_key(self):
        decrypted_api_key = get_decrypted_key(self.api_key_obj.api_key)
        self.assertFalse(decrypted_api_key == self.api_key_obj.api_key)

    def test_encrypt_api_key(self):
        encrypted_api_key = get_encrypted_key('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3')
        self.assertTrue(encrypted_api_key != 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3')

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

        self.assertEqual(unique_articles, [{'brand': 'Hanes Store', 'nm_id': 129494856},
                                           {'brand': 'Hanes Store', 'nm_id': 129494851},
                                           {'brand': 'Hanes Store', 'nm_id': 129494822}])

    def test_generating_unique_reports(self):
        unique_reports = get_unique_reports(self.sale_objects)

        self.assertEqual(unique_reports, {19279748, 19279741})

    def test_generating_user_products_data(self):
        article_obj_list = []

        for article_data in self.articles_data:
            handle_article_additional_data(article_data.get('nm_id'), article_data.get('brand'), article_obj_list)

        self.assertEqual(len(article_obj_list), 5)
        self.assertEqual(article_obj_list[0].get('nm_id'), 94212294)
        self.assertEqual(article_obj_list[0].get('title'), 'Щетки стеклоочистителя')
        self.assertEqual(
            article_obj_list[0].get('img'),
            'https://basket-05.wb.ru//vol942/part94212/94212294/images/tm/1.jpg'
        )

    def test_generating_user_products(self):
        unique_articles = get_unique_articles(self.sale_objects)

        generate_user_products(self.user, unique_articles, self.api_key_obj)
        user_products_count_1 = ClientUniqueProduct.objects.filter(api_key=self.api_key_obj).count()

        """ Test duplicates of ClientUniqueProduct handled correctly """
        generate_user_products(self.user, unique_articles, self.api_key_obj)
        user_products_count_2 = ClientUniqueProduct.objects.filter(api_key=self.api_key_obj).count()

        self.assertEqual(user_products_count_1, 3)
        self.assertEqual(user_products_count_2, 3)

    def test_successful_generating_incorrect_reports(self):
        generate_incorrect_reports(self.user, test_incorrect_reports_data, self.api_key_obj)
        incorrect_reports_count_1 = IncorrectReport.objects.filter(api_key=self.api_key_obj, owner=self.user).count()

        generate_incorrect_reports(self.user, [], self.api_key_obj)
        incorrect_reports_count_3 = IncorrectReport.objects.filter(api_key=self.api_key_obj, owner=self.user).count()

        self.assertEqual(incorrect_reports_count_1, 3)
        self.assertEqual(incorrect_reports_count_3, 0)

    def test_duplicates_of_incorrectreport_handled_correctly(self):
        generate_incorrect_reports(self.user, test_incorrect_reports_data, self.api_key_obj)
        incorrect_reports_count_1 = IncorrectReport.objects.filter(api_key=self.api_key_obj, owner=self.user).count()

        generate_incorrect_reports(self.user, test_incorrect_reports_data, self.api_key_obj)
        incorrect_reports_count_2 = IncorrectReport.objects.filter(api_key=self.api_key_obj, owner=self.user).count()

        self.assertEqual(incorrect_reports_count_1, 3)
        self.assertEqual(incorrect_reports_count_2, 3)

    def test_generating_reports(self):
        generate_reports(self.user, self.api_key_obj)

        reports_objs_count_1 = SaleReport.objects.filter(
            api_key__is_current=True,
            api_key__user=self.user,
        ).count()

        report_obj = SaleReport.objects.filter(
            api_key__is_current=True,
            api_key__user=self.user,
        ).first()

        self.assertEqual(reports_objs_count_1, 2)
        self.assertEqual(report_obj.api_key, self.api_key_obj)
        self.assertEqual(report_obj.owner, self.user)
        self.assertEqual(report_obj.realizationreport_id, 19279741)
        self.assertEqual(report_obj.year, 2022)
        self.assertEqual(report_obj.month_num, 10)
        self.assertEqual(report_obj.create_dt, datetime(2022, 11, 7, 11, 31, 43, tzinfo=timezone.utc))
        self.assertEqual(report_obj.date_from, datetime(2022, 10, 31, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(report_obj.date_to, datetime(2022, 11, 6, 0, 0, tzinfo=timezone.utc))

    def test_duplicates_of_salereport_handled_correctly(self):
        generate_reports(self.user, self.api_key_obj)

        reports_objs_count_1 = SaleReport.objects.filter(
            api_key__is_current=True,
            api_key__user=self.user,
        ).count()

        generate_reports(self.user, self.api_key_obj)

        reports_objs_count_2 = SaleReport.objects.filter(
            api_key__is_current=True,
            api_key__user=self.user,
        ).count()

        self.assertEqual(reports_objs_count_1, 2)
        self.assertEqual(reports_objs_count_2, 2)

    def test_check_validity_condition_of_invalid_report(self):
        test_validation_result = check_sale_obj_validation(self.invalid_sale_objects[3])

        self.assertEqual(test_validation_result, True)

    def test_successful_check_sale_obj_validation(self):
        test_validation_result = check_sale_obj_validation(self.sale_objects[1])

        self.assertEqual(test_validation_result, True)

    def test_unsuccessful_check_sale_obj_validation(self):
        test_validation_result = check_sale_obj_validation(self.invalid_sale_objects[0])

        self.assertEqual(test_validation_result.get('realizationreport_id'), 19279748)
        self.assertEqual(test_validation_result.get('incorrect_report_data').get('date_from'), None)
        self.assertEqual(test_validation_result.get('incorrect_report_data').get('date_to'), "2022-11-06T00:00:00Z")

    def test_validation_with_invalid_reports(self):
        test_validation_result = get_incorrect_reports_lst(self.invalid_sale_objects)

        self.assertEqual(test_validation_result, {
            'realizationreport_ids': [19279748, 19279728],
            'incorrect_reports_data_list': [
                {
                    'realizationreport_id': 19279748,
                    'date_from': None,
                    'date_to': '2022-11-06T00:00:00Z'
                },
                {
                    'realizationreport_id': 19279728,
                    'date_from': '2022-10-31T00:00:00Z',
                    'date_to': '2022-11-06T00:00:00Z'
                }
            ]
        })

    def test_validation_with_valid_reports(self):
        test_validation_result = get_incorrect_reports_lst(self.sale_objects)

        self.assertEqual(test_validation_result, {
            'realizationreport_ids': [],
            'incorrect_reports_data_list': []
        })



