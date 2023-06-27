import uuid
from datetime import datetime
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta

from payments.services.generating_subscribed_to_date import get_subscribed_to_date
from users.models import ClientUniqueProduct, SaleReport, UnloadedReports, IncorrectReport, SaleObject
from users.services.decrypt_api_key_service import get_decrypted_key
from users.services.encrypt_api_key_service import get_encrypted_key
from users.services.generate_excel_net_costs_example_service import generate_excel_net_costs_example
from users.services.generate_last_report_date_service import get_last_report_date, generate_date_by_months_filter
from users.services.generate_subscriptions_data_service import get_user_subscriptions_data, \
    get_calculated_subscription_values
from users.services.wb_request_handling_services.execute_request_data_handling import get_existing_products, \
    get_existing_reports_ids, execute_wildberries_request_data_handling
from users.services.wb_request_handling_services.generating_incorrect_reports_service import \
    create_incorrect_reports
from users.services.wb_request_handling_services.generating_products_objs_service import generate_user_products
from users.services.wb_request_handling_services.generating_sale_objects_service import create_sale_objects
from users.services.wb_request_handling_services.generating_unique_respose_data_services import \
    get_sorted_unique_report_ids, get_unique_nm_ids
from users.services.wb_request_handling_services.generating_user_reports_service import generate_reports
from users.services.wb_request_handling_services.handling_wildberries_request_services import \
    get_filtered_wildberries_response, get_wildberries_response
from users.services.wb_request_handling_services.reports_validation_services import get_incorrect_reports
from users.tests.users_pytest_fixtures import (
    test_password, test_subscriptions_data, create_user, create_subscription_types, create_user_discount,
    create_user_subscription, create_api_key, create_client_unique_product, test_products,
    test_incorrect_reports, test_sales, create_user_report, test_invalid_sales, test_sales_with_exception, test_api_key,
    user_factory, api_key_factory, fake_wb_response_data, product_factory, report_factory, incorrect_report_factory,
)

import pytest
import pandas as pd
import numpy as np
from openpyxl import Workbook


pytestmark = pytest.mark.django_db


@pytest.fixture
def test_encrypted_api_key(test_api_key):
    return get_encrypted_key(test_api_key)


@pytest.fixture
def test_decrypted_api_key(test_encrypted_api_key):
    return get_decrypted_key(test_encrypted_api_key)


def test_decrypted_api_key_func(test_api_key, test_decrypted_api_key, test_encrypted_api_key):
    assert test_decrypted_api_key == test_api_key
    assert test_decrypted_api_key != test_encrypted_api_key


def test_encrypted_api_key_func(test_api_key, test_encrypted_api_key, test_decrypted_api_key):
    assert test_encrypted_api_key != test_api_key
    assert test_encrypted_api_key != test_decrypted_api_key


def test_generate_excel_net_costs_example():
    data = [(12, Decimal(12.2), datetime(2022, 12, 25))]

    net_costs_example_result = generate_excel_net_costs_example(data)

    assert type(net_costs_example_result) == Workbook


def test_generate_date_by_months_filter():
    past_months_date = date.today() - relativedelta(months=3)
    first_date_of_month = past_months_date.replace(day=1)
    year = first_date_of_month.year - 1 if first_date_of_month.isocalendar()[1] == 52 else first_date_of_month.year
    last_report_date_test = date.fromisocalendar(
        year,
        first_date_of_month.isocalendar()[1],
        1
    ).strftime('%Y-%m-%d')

    last_report_date_result = generate_date_by_months_filter(3)

    assert last_report_date_result == last_report_date_test


def test_get_last_report_date_without_created_reports(create_user, create_api_key):
    user = create_user()
    api_key = create_api_key(user=user)

    past_months_date = date.today() - relativedelta(months=3)
    first_date_of_month = past_months_date.replace(day=1)
    year = first_date_of_month.year - 1 if first_date_of_month.isocalendar()[1] == 52 else first_date_of_month.year
    last_report_date_test = date.fromisocalendar(
        year,
        first_date_of_month.isocalendar()[1],
        1
    ).strftime('%Y-%m-%d')

    last_report_date = get_last_report_date(api_key)

    assert last_report_date == last_report_date_test


def test_get_last_report_date_with_sale_report(create_user, create_api_key, create_user_report):
    user = create_user()
    api_key = create_api_key(user=user, is_wb_data_loaded=True)
    create_dt = datetime.now()

    create_user_report(
        api_key=api_key,
        owner=user,
        realizationreport_id=28856935,
        week_num=2,
        month_num=12,
        unique_week_uuid=uuid.uuid4(),
        create_dt=create_dt,
        date_from=datetime.now(),
        date_to=datetime.now()
    )

    last_report_date = get_last_report_date(api_key)

    assert last_report_date == create_dt.strftime('%Y-%m-%d')


def test_get_last_report_date_with_incorrect_report(create_user, create_api_key, incorrect_report_factory):
    user = create_user()
    api_key = create_api_key(user=user, is_wb_data_loaded=True)
    create_dt = datetime.now()

    incorrect_report_factory(
        api_key=api_key,
        owner=user,
        realizationreport_id=28856935,
        date_from=datetime.now(),
        date_to=datetime.now()
    )

    last_report_date = get_last_report_date(api_key)

    assert last_report_date == create_dt.strftime('%Y-%m-%d')


def test_get_user_subscriptions_data(create_user, create_subscription_types):
    user = create_user()
    subscription_types_objects = create_subscription_types

    user_subscription_data = get_user_subscriptions_data(user)

    assert len(user_subscription_data) == len(subscription_types_objects)
    assert all(type(data_dict) is dict for data_dict in user_subscription_data)


def test_get_calculated_subscription_values_with_default_data(create_user, create_subscription_types):
    user = create_user()
    subscription_types_objects = create_subscription_types

    calculated_subscription_values = get_calculated_subscription_values(subscription_types_objects[0], None, None)

    assert calculated_subscription_values.get('build_in_discount') == subscription_types_objects[0].build_in_discount
    assert calculated_subscription_values.get('cost') == subscription_types_objects[0].build_in_discount
    assert calculated_subscription_values.get('cost_for_week') == 0
    assert calculated_subscription_values.get('subscribed_to') is None
    assert calculated_subscription_values.get('is_active') is False
    assert calculated_subscription_values.get('is_test_period') is True


def test_get_calculated_subscription_values_with_additional_data_1(
        create_user,
        create_subscription_types,
        create_user_discount,
        create_user_subscription
):
    user = create_user()
    subscription_types_objects = create_subscription_types
    user_discount = create_user_discount(user=user, percent=30, expiration_date=datetime(2024, 3, 12, 12, 59))

    user_subscription = create_user_subscription(
        subscription_type=subscription_types_objects[2],
        user=user,
        subscribed_from=datetime.now(),
        total_cost=9240,
        subscribed_to=get_subscribed_to_date(
            subscription_types_objects[2].duration,
            subscription_types_objects[2].duration_desc
        )

    )

    calculated_subscription_values = get_calculated_subscription_values(
        subscription_types_objects[2], user_subscription, user_discount)

    assert calculated_subscription_values.get('build_in_discount') == user_discount.percent
    assert calculated_subscription_values.get('cost') == 9240
    assert calculated_subscription_values.get('cost_for_week') == 770
    assert calculated_subscription_values.get('subscribed_to') == user_subscription.subscribed_to
    assert calculated_subscription_values.get('is_active') is True
    assert calculated_subscription_values.get('is_test_period') is False


def test_get_calculated_subscription_values_with_additional_data_2(
        create_user,
        create_subscription_types,
        create_user_discount,
        create_user_subscription
):
    user = create_user()
    subscription_types_objects = create_subscription_types
    user_discount = create_user_discount(user=user, percent=50, expiration_date=datetime(2024, 3, 12, 12, 59))

    user_subscription = create_user_subscription(
        subscription_type=subscription_types_objects[3],
        user=user,
        subscribed_from=datetime.now(),
        total_cost=6600,
        subscribed_to=get_subscribed_to_date(
            subscription_types_objects[3].duration,
            subscription_types_objects[3].duration_desc
        )

    )

    calculated_subscription_values = get_calculated_subscription_values(
        subscription_types_objects[2], user_subscription, user_discount)

    assert calculated_subscription_values.get('build_in_discount') == user_discount.percent
    assert calculated_subscription_values.get('cost') == 6600
    assert calculated_subscription_values.get('cost_for_week') == 550
    assert calculated_subscription_values.get('subscribed_to') is None
    assert calculated_subscription_values.get('is_active') is False
    assert calculated_subscription_values.get('is_test_period') is False


def test_get_filtered_wildberries_response(api_key_factory, fake_wb_response_data):
    api_key = api_key_factory()

    response = pd.DataFrame(fake_wb_response_data)

    expected_response = pd.DataFrame(
        [
            {'realizationreport_id': 34714186, 'nm_id': 123},
            {'realizationreport_id': 31427431, 'nm_id': 123},
            {'realizationreport_id': 29953976, 'nm_id': 123},
            {'realizationreport_id': 29953977, 'nm_id': 123}
        ]
    )

    filtered_response = get_filtered_wildberries_response(api_key, response)

    expected_response.reset_index(drop=True, inplace=True)
    filtered_response.reset_index(drop=True, inplace=True)

    assert filtered_response.equals(expected_response)
    assert UnloadedReports.objects.all().count() == 2
    assert UnloadedReports.objects.filter(realizationreport_id__in=[35672809, 35672810]).exists()


def test_get_wildberries_response_with_error_status(api_key_factory, mocker):
    api_key = api_key_factory()

    mocker.patch(
        "users.services.wb_request_handling_services.handling_wildberries_request_services.send_request_for_sales",
        return_value={"status": False, "message": 'Test message'}
    )

    response = get_wildberries_response(api_key, '2022-12-20', '2023-10-11')

    assert response == {"status": False, "message": 'Test message'}


def test_get_wildberries_response_with_few_sales(api_key_factory, fake_wb_response_data, mocker):
    api_key = api_key_factory()

    mocker.patch(
        "users.services.wb_request_handling_services.handling_wildberries_request_services.send_request_for_sales",
        return_value={
            "status": True,
            "data": fake_wb_response_data
        }
    )

    expected_response: pd.DataFrame = pd.DataFrame(fake_wb_response_data)

    response: pd.DataFrame = get_wildberries_response(api_key, '2022-12-20', '2023-10-11')

    assert response.equals(expected_response)


def test_get_wildberries_response_with_100_thousand_sales(api_key_factory, fake_wb_response_data, mocker):
    api_key = api_key_factory()

    fake_data = [{"realizationreport_id": num / 2, "test": 'test'} for num in range(100000)]

    mocker.patch(
        "users.services.wb_request_handling_services.handling_wildberries_request_services.send_request_for_sales",
        return_value={
            "status": True,
            "data": fake_data + fake_wb_response_data
        }
    )

    response: pd.DataFrame = get_wildberries_response(api_key, '2022-12-20', '2023-10-11')

    assert '35672809' not in response['realizationreport_id'].values \
           and '35672810' not in response['realizationreport_id'].values
    assert UnloadedReports.objects.all().count() == 2
    assert UnloadedReports.objects.filter(realizationreport_id__in=[35672809, 35672810]).exists()


def test_get_sorted_unique_report_ids():
    expected_report_ids: np.ndarray = np.array([34714186, 35672809, 35672810])
    fake_response_data_frame = pd.DataFrame([
        {"realizationreport_id": 35672809},
        {"realizationreport_id": 35672809},
        {"realizationreport_id": 35672810},
        {"realizationreport_id": 34714186},
        {"realizationreport_id": 34714186},
    ])
    sorted_report_ids: np.ndarray = get_sorted_unique_report_ids(fake_response_data_frame)

    assert np.array_equal(sorted_report_ids, expected_report_ids)


def test_get_unique_nm_ids():
    expected_nm_ids = np.array([35672809, 35672810, 34714186])

    fake_response_data_frame = pd.DataFrame([
        {"nm_id": 35672809},
        {"nm_id": 35672809},
        {"nm_id": 35672810},
        {"nm_id": 35672810},
        {"nm_id": 34714186},
        {"nm_id": None},  # This nm_id (None) should be excluded
        {"nm_id": 99866376}  # This nm_id (99866376) should be excluded
    ])

    unique_nm_ids = get_unique_nm_ids(fake_response_data_frame)

    assert np.array_equal(unique_nm_ids, expected_nm_ids)


def test_get_incorrect_reports_with_valid_sales(test_sales):
    sales = pd.DataFrame(test_sales)
    incorrect_reports: pd.DataFrame = get_incorrect_reports(sales)

    assert len(incorrect_reports) == 0


def test_get_incorrect_reports_with_condition_1():
    sales = pd.DataFrame([
        {
            "realizationreport_id": 27982018,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": None,
            "gi_id": None,
            "subject_name": None,
            "nm_id": None,
            "brand_name": None,
            "sa_name": None,
            "ts_name": "39",
            "barcode": "2036379766665",
            "doc_type_name": "Продажа",
            "quantity": 0,
            "retail_price": 7500,
            "retail_amount": None,
            "sale_percent": 30,
            "commission_percent": None,
            "office_name": "Коледино",
            "supplier_oper_name": "Логистика",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": None,
            "shk_id": 6483881955,
            "retail_price_withdisc_rub": 0,
            "delivery_amount": 0,
            "return_amount": 0,
            "delivery_rub": 10,
            "gi_box_type_name": "Без коробов",
            "product_discount_for_report": 30,
            "supplier_promo": 0,
            "rid": None,
            "ppvz_spp_prc": 0.1746,
            "ppvz_kvw_prc_base": 0.1917,
            "ppvz_kvw_prc": 0.0171,
            "ppvz_sales_commission": 89.58,
            "ppvz_for_pay": 0,
            "ppvz_reward": 176.38,
            "acquiring_fee": None,
            "acquiring_bank": "Сбербанк Росси 7707083893",
            "ppvz_vw": -122.08,
            "ppvz_vw_nds": -24.42,
            "ppvz_office_id": 202886,
            "ppvz_supplier_id": 369039,
            "ppvz_supplier_name": "ООО \"СОЮЗ\"",
            "ppvz_inn": "2511117161",
            "declaration_number": "",
            "sticker_id": "",
            "site_country": "RU",
            "penalty": 0,
            "additional_payment": None,
            "srid": "36143466073767957.0.0"
        }
    ])

    incorrect_reports: pd.DataFrame = get_incorrect_reports(sales)

    assert len(incorrect_reports) == 0


def test_get_incorrect_reports_with_condition_2():
    sales = pd.DataFrame([
        {
            "realizationreport_id": 27982018,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": None,
            "gi_id": None,
            "subject_name": "test",
            "nm_id": 11597805863,
            "brand_name": None,
            "sa_name": None,
            "ts_name": "39",
            "barcode": "2036379766665",
            "doc_type_name": "Продажа",
            "quantity": 1,
            "retail_price": 7500,
            "retail_amount": 123,
            "sale_percent": 30,
            "commission_percent": 0.23,
            "office_name": "Коледино",
            "supplier_oper_name": "Логистика",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": None,
            "shk_id": 6483881955,
            "retail_price_withdisc_rub": 0,
            "delivery_amount": None,
            "return_amount": 0,
            "delivery_rub": 10,
            "gi_box_type_name": "Без коробов",
            "product_discount_for_report": 30,
            "supplier_promo": 0,
            "rid": None,
            "ppvz_spp_prc": 0.1746,
            "ppvz_kvw_prc_base": 0.1917,
            "ppvz_kvw_prc": 0.0171,
            "ppvz_sales_commission": 89.58,
            "ppvz_for_pay": 0,
            "ppvz_reward": 176.38,
            "acquiring_fee": 35.28,
            "acquiring_bank": "Сбербанк Росси 7707083893",
            "ppvz_vw": -122.08,
            "ppvz_vw_nds": -24.42,
            "ppvz_office_id": 202886,
            "ppvz_supplier_id": 369039,
            "ppvz_supplier_name": "ООО \"СОЮЗ\"",
            "ppvz_inn": "2511117161",
            "declaration_number": "",
            "sticker_id": "",
            "site_country": None,
            "penalty": None,
            "additional_payment": None,
            "srid": "36143466073767957.0.0"
        }
    ])

    incorrect_reports: pd.DataFrame = get_incorrect_reports(sales)

    assert len(incorrect_reports) == 0


def test_get_incorrect_reports_with_condition_3():
    sales = pd.DataFrame([
        {
            "realizationreport_id": None,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": 11597805863,
            "gi_id": 7997454,
            "subject_name": None,
            "nm_id": None,
            "brand_name": None,
            "sa_name": "К-5023/17К-5023/17",
            "ts_name": "39",
            "barcode": "2036379766665",
            "doc_type_name": "Продажа",
            "quantity": 1,
            "retail_price": 7500,
            "retail_amount": 123,
            "sale_percent": 30,
            "commission_percent": 0.23,
            "office_name": "Коледино",
            "supplier_oper_name": "Возмещение издержек по перевозке",
            "order_dt": None,
            "sale_dt": None,
            "rr_dt": "2023-03-12T00:00:00Z",
            "shk_id": 6483881955,
            "retail_price_withdisc_rub": None,
            "delivery_amount": None,
            "return_amount": None,
            "delivery_rub": None,
            "gi_box_type_name": "Без коробов",
            "product_discount_for_report": None,
            "supplier_promo": None,
            "rid": None,
            "ppvz_spp_prc": 0.1746,
            "ppvz_kvw_prc_base": 0.1917,
            "ppvz_kvw_prc": 0.0171,
            "ppvz_sales_commission": 89.58,
            "ppvz_for_pay": 0,
            "ppvz_reward": 176.38,
            "acquiring_fee": 35.28,
            "acquiring_bank": "Сбербанк Росси 7707083893",
            "ppvz_vw": -122.08,
            "ppvz_vw_nds": -24.42,
            "ppvz_office_id": 202886,
            "ppvz_supplier_id": 369039,
            "ppvz_supplier_name": "ООО \"СОЮЗ\"",
            "ppvz_inn": "2511117161",
            "declaration_number": "",
            "sticker_id": None,
            "site_country": None,
            "penalty": None,
            "additional_payment": None,
            "srid": None
        }
    ])

    incorrect_reports: pd.DataFrame = get_incorrect_reports(sales)

    assert len(incorrect_reports) == 0


def test_get_incorrect_reports_with_invalid_sales(test_invalid_sales):
    sales = pd.DataFrame(test_invalid_sales)

    incorrect_reports: pd.DataFrame = get_incorrect_reports(sales)

    assert len(incorrect_reports) == 3


def test_generate_user_products(api_key_factory, user_factory, test_products, mocker):
    user = user_factory()
    api_key = api_key_factory(user=user)

    # A list is used rather than a tuple, since a tuple is disordered and the elements are formed in a chaotic order
    test_articles_set = {141371096, 141972556, 140930947, 141370942}

    mocker.patch(
        'users.services.wb_request_handling_services.generating_user_products_data_service.handle_article_additional_data',
        return_value=[
            {"brand": "Hanes Store", "title": "Носки женские короткие набор белые черные хлопок"},
            {"brand": "Hanes Store", "title": "Носки женские короткие набор белые черные хлопок"},
            {"brand": "Hanes Store", "title": "Носки женские короткие белые 1 пара"},
            {"brand": "Hanes Store", "title": "Носки женские короткие набор белые черные хлопок"},
        ]
    )

    generate_user_products(user, test_articles_set, api_key)

    generated_user_products_status = [
        api_key.api_key_products.filter(
            nm_id=product.get("nm_id"),
            brand=product.get("brand"),
            image=product.get("image"),
            product_name=product.get("product_name")
        ).exists() for product in test_products
    ]

    assert api_key.api_key_products.count() == 4
    assert api_key.is_products_loaded
    assert all(generated_user_products_status)


def test_duplicates_generate_user_products(
        api_key_factory,
        user_factory,
        test_products,
        create_client_unique_product,
        mocker
):
    user = user_factory()
    api_key = api_key_factory(user=user)

    # A list is used rather than a tuple, since a tuple is disordered and the elements are formed in a chaotic order
    test_articles_set = {141371096, 141972556, 140930947, 141370942}
    for product in test_products:
        create_client_unique_product(
            api_key=api_key,
            nm_id=product.get("nm_id"),
            brand=product.get("brand"),
            image=product.get("image"),
            product_name=product.get("product_name")
        )

    mocker.patch(
        'users.services.wb_request_handling_services.generating_user_products_data_service.handle_article_additional_data',
        return_value=[
            {"brand": "Hanes Store", "title": "Носки женские короткие набор белые черные хлопок"},
            {"brand": "Hanes Store", "title": "Носки женские короткие набор белые черные хлопок"},
            {"brand": "Hanes Store", "title": "Носки женские короткие белые 1 пара"},
            {"brand": "Hanes Store", "title": "Носки женские короткие набор белые черные хлопок"},
        ]
    )
    generate_user_products(user, test_articles_set, api_key)

    assert api_key.api_key_products.count() == 4


def test_get_existing_products(product_factory):
    nm_ids = [123123123]
    product_factory(nm_id=nm_ids[0])

    products = get_existing_products(nm_ids)

    assert products.get(nm_ids[0])


def test_get_existing_reports_ids(api_key_factory, user_factory, report_factory):
    user = user_factory()
    api_key = api_key_factory(user=user)
    fake_report_ids = [1, 2, 3, 4, 5]
    for report_id in fake_report_ids:
        report_factory(realizationreport_id=report_id, owner=user, api_key=api_key)

    report_ids = get_existing_reports_ids(user, api_key)

    assert list(report_ids) == fake_report_ids


def test_create_incorrect_reports(api_key_factory, user_factory):
    user = user_factory()
    api_key = api_key_factory(user=user)

    fake_incorrect_reports = pd.DataFrame([
        {
            "realizationreport_id": 1234567,
            "date_from": "2023-10-15",
            "date_to":  "2023-10-15"
        },
        {
            "realizationreport_id": 123456789,
            "date_from": "2023-10-15",
            "date_to": "2023-10-15"
        },
    ])

    create_incorrect_reports(user, api_key, fake_incorrect_reports)

    assert IncorrectReport.objects.count() == 2
    assert IncorrectReport.objects.filter(realizationreport_id=1234567).exists()


def test_create_duplicates_incorrect_reports(api_key_factory, user_factory, incorrect_report_factory):
    user = user_factory()
    api_key = api_key_factory(user=user)

    incorrect_report_factory(realizationreport_id=1234567, owner=user, api_key=api_key)

    fake_incorrect_reports = pd.DataFrame([
        {
            "realizationreport_id": 1234567,
            "date_from": "2023-10-15",
            "date_to": "2023-10-15"
        },
    ])

    create_incorrect_reports(user, api_key, fake_incorrect_reports)

    assert IncorrectReport.objects.count() == 1
    assert IncorrectReport.objects.filter(realizationreport_id=1234567).exists()


def test_empty_create_incorrect_reports(api_key_factory, user_factory, incorrect_report_factory):
    user = user_factory()
    api_key = api_key_factory(user=user)

    incorrect_report_factory(realizationreport_id=1234567, owner=user, api_key=api_key)

    create_incorrect_reports(user, api_key, pd.DataFrame([]))

    assert IncorrectReport.objects.count() == 0


def test_create_sale_objects(api_key_factory, user_factory, test_sales, product_factory):
    user = user_factory()
    api_key = api_key_factory(user=user)
    nm_ids = [141371096, 141972556, 140930947, 141370942]
    for nm_id in nm_ids:
        product_factory(nm_id=nm_id)

    existing_products = ClientUniqueProduct.objects.in_bulk(nm_ids, field_name='nm_id')
    existing_reports_ids = []
    incorrect_reports_ids = []

    sales_data_frame: pd.DataFrame = pd.DataFrame(test_sales)

    create_sale_objects(user, api_key, sales_data_frame, existing_reports_ids, incorrect_reports_ids, existing_products)

    assert SaleObject.objects.count() == 4


def test_create_sale_objects_with_empty_sales(api_key_factory, user_factory):
    user = user_factory()
    api_key = api_key_factory(user=user)

    sales_data_frame = pd.DataFrame([])
    sales_creation_status = create_sale_objects(user, api_key, sales_data_frame, [], [], {})

    assert sales_creation_status == {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }


def test_create_sale_objects_with_existing_reports(api_key_factory, user_factory, test_sales, product_factory):
    user = user_factory()
    api_key = api_key_factory(user=user)
    nm_ids = [141371096, 141972556, 140930947, 141370942]
    for nm_id in nm_ids:
        product_factory(nm_id=nm_id)

    existing_products = ClientUniqueProduct.objects.in_bulk(nm_ids, field_name='nm_id')
    existing_reports_ids = [27982018]
    incorrect_reports_ids = []

    sales_data_frame: pd.DataFrame = pd.DataFrame(test_sales)

    create_sale_objects(user, api_key, sales_data_frame, existing_reports_ids, incorrect_reports_ids, existing_products)

    assert not SaleObject.objects.filter(realizationreport_id=27982018).exists()
    assert SaleObject.objects.count() == 3


def test_create_sale_objects_with_incorrect_reports(api_key_factory, user_factory, test_sales, product_factory):
    user = user_factory()
    api_key = api_key_factory(user=user)
    nm_ids = [141371096, 141972556, 140930947, 141370942]
    for nm_id in nm_ids:
        product_factory(nm_id=nm_id)

    existing_products = ClientUniqueProduct.objects.in_bulk(nm_ids, field_name='nm_id')
    existing_reports_ids = []
    incorrect_reports_ids = [27982018]

    sales_data_frame: pd.DataFrame = pd.DataFrame(test_sales)

    create_sale_objects(user, api_key, sales_data_frame, existing_reports_ids, incorrect_reports_ids, existing_products)

    assert not SaleObject.objects.filter(realizationreport_id=27982018).exists()
    assert SaleObject.objects.count() == 3


def test_generate_reports_without_sales(
        api_key_factory,
        user_factory,
):
    user = user_factory()
    api_key = api_key_factory(user=user)

    generate_reports(
        user,
        api_key
    )

    assert SaleReport.objects.filter(api_key=api_key).count() == 0


def test_generate_reports_with_sales(
        api_key_factory,
        user_factory,
        test_sales,
        product_factory,
):
    user = user_factory()
    api_key = api_key_factory(user=user)

    nm_ids = [141371096, 141972556, 140930947, 141370942]
    for nm_id in nm_ids:
        product_factory(nm_id=nm_id)

    existing_products = ClientUniqueProduct.objects.in_bulk(nm_ids, field_name='nm_id')
    existing_reports_ids = []
    incorrect_reports_ids = []

    sales_data_frame: pd.DataFrame = pd.DataFrame(test_sales)

    create_sale_objects(user, api_key, sales_data_frame, existing_reports_ids, incorrect_reports_ids, existing_products)

    generate_reports(
        user,
        api_key
    )

    assert SaleReport.objects.filter(api_key=api_key).count() == 4


def test_duplicates_generate_reports(
        api_key_factory,
        user_factory,
        test_sales,
        product_factory,
):
    user = user_factory()
    api_key = api_key_factory(user=user)

    nm_ids = [141371096, 141972556, 140930947, 141370942]
    for nm_id in nm_ids:
        product_factory(nm_id=nm_id)

    existing_products = ClientUniqueProduct.objects.in_bulk(nm_ids, field_name='nm_id')
    existing_reports_ids = []
    incorrect_reports_ids = []

    sales_data_frame: pd.DataFrame = pd.DataFrame(test_sales)

    create_sale_objects(user, api_key, sales_data_frame, existing_reports_ids, incorrect_reports_ids, existing_products)

    for i in range(2):
        generate_reports(
            user,
            api_key
        )

    assert SaleReport.objects.filter(api_key=api_key).count() == 4


def test_execute_wildberries_request_data_handling(api_key_factory, user_factory, test_sales, mocker):
    user = user_factory()
    api_key = api_key_factory(user=user)

    mocker.patch(
        "users.services.wb_request_handling_services.handling_wildberries_request_services.send_request_for_sales",
        return_value={
            "status": True,
            "data": test_sales
        }
    )

    mocker.patch(
        'users.services.wb_request_handling_services.generating_user_products_data_service.handle_article_additional_data',
        return_value=None
    )

    request_handling_status = execute_wildberries_request_data_handling(user, '2022-12-10', '2023-01-11', api_key)

    assert SaleObject.objects.filter(owner=user).count() == 4
    assert ClientUniqueProduct.objects.filter(api_key=api_key).count() == 4
    assert SaleReport.objects.filter(owner=user).count() == 4









