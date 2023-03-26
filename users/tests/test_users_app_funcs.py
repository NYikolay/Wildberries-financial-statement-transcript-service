from datetime import datetime
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta

from payments.services.generating_subscribed_to_date import get_subscribed_to_date
from users.models import ClientUniqueProduct, SaleReport
from users.services.decrypt_api_key_service import get_decrypted_key
from users.services.encrypt_api_key_service import get_encrypted_key
from users.services.generate_excel_net_costs_example_service import generate_excel_net_costs_example
from users.services.generate_last_report_date_service import get_last_report_date, generate_date_by_months_filter
from users.services.generate_subscriptions_data_service import get_user_subscriptions_data, \
    get_calculated_subscription_values, generate_robokassa_form
from users.services.wb_request_hanling_services.generating_incorrect_reports_service import generate_incorrect_reports
from users.services.wb_request_hanling_services.generating_products_objs_service import generate_user_products
from users.services.wb_request_hanling_services.generating_sale_objects_service import create_sale_objects
from users.services.wb_request_hanling_services.generating_unique_articles_service import get_unique_articles
from users.services.wb_request_hanling_services.generating_unique_reports_service import get_unique_reports
from users.services.wb_request_hanling_services.generating_user_products_data_service import send_request_for_card_json
from users.services.wb_request_hanling_services.generating_user_reports_service import generate_reports
from users.services.wb_request_hanling_services.reports_validation_service import check_sale_obj_validation
from users.tests.pytest_fixtures import (
    test_password, test_subscriptions_data, create_user, create_subscription_types, create_user_discount,
    create_user_subscription, create_api_key, create_incorrect_reports, create_client_unique_product, test_products,
    test_incorrect_reports, test_sales, create_user_report, test_invalid_sales, test_sales_with_exception
)

import pytest
from openpyxl import Workbook


@pytest.fixture
def test_api_key():
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjBlNTE5YmEwLWRmMGMtNGY1NC04ZWU2'


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


def test_get_last_report_date():
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


@pytest.mark.django_db
def test_get_user_subscriptions_data(create_user, create_subscription_types):
    user = create_user()
    subscription_types_objects = create_subscription_types

    user_subscription_data = get_user_subscriptions_data(user)

    assert len(user_subscription_data) == len(subscription_types_objects)
    assert all(type(data_dict) is dict for data_dict in user_subscription_data)


@pytest.mark.django_db
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


@pytest.mark.django_db
def test_get_calculated_subscription_values_with_additional_data_1(
        create_user,
        create_subscription_types,
        create_user_discount,
        create_user_subscription
):
    user = create_user()
    subscription_types_objects = create_subscription_types
    user_discount = create_user_discount(user=user, percent=30)

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


@pytest.mark.django_db
def test_get_calculated_subscription_values_with_additional_data_2(
        create_user,
        create_subscription_types,
        create_user_discount,
        create_user_subscription
):
    user = create_user()
    subscription_types_objects = create_subscription_types
    user_discount = create_user_discount(user=user, percent=50)

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


@pytest.mark.django_db
def test_generate_incorrect_reports(create_user, create_api_key, test_incorrect_reports):
    user = create_user()
    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )

    generate_incorrect_reports(user, test_incorrect_reports, api_key)

    generated_incorrect_reports_status = [api_key.unavailable_api_key_reports.filter(
        realizationreport_id=report.get('realizationreport_id'),
        date_from=report.get('date_from'),
        date_to=report.get('date_to')
    ).exists() for report in test_incorrect_reports]

    assert api_key.unavailable_api_key_reports.count() == 3
    assert all(generated_incorrect_reports_status)


@pytest.mark.django_db
def test_duplicates_generate_incorrect_reports(
        create_user,
        create_api_key,
        create_incorrect_reports,
        test_incorrect_reports
):
    user = create_user()
    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )

    for report in test_incorrect_reports:
        create_incorrect_reports(
            api_key=api_key,
            owner=user,
            realizationreport_id=report.get("realizationreport_id"),
            date_from=report.get("date_from"),
            date_to=report.get("date_to")
        )

    generate_incorrect_reports(user, test_incorrect_reports, api_key)

    assert api_key.unavailable_api_key_reports.count() == 3


@pytest.mark.django_db
def test_deleting_generate_incorrect_reports(
        create_user,
        create_api_key,
        create_incorrect_reports,
        test_incorrect_reports
):

    user = create_user()
    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )

    create_incorrect_reports(
        api_key=api_key,
        owner=user,
        realizationreport_id=test_incorrect_reports[0].get("realizationreport_id"),
        date_from=test_incorrect_reports[0].get("date_from"),
        date_to=test_incorrect_reports[0].get("date_to")
    )

    generate_incorrect_reports(user, [], api_key)

    assert api_key.unavailable_api_key_reports.count() == 0


@pytest.mark.django_db
def test_generate_user_products(create_user, create_api_key, test_products):
    user = create_user()
    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )

    generate_user_products(user, test_products, api_key)

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


@pytest.mark.django_db
def test_duplicates_generate_user_products(create_user, create_api_key, test_products, create_client_unique_product):
    user = create_user()
    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )

    for product in test_products:
        create_client_unique_product(
            api_key=api_key,
            nm_id=product.get("nm_id"),
            brand=product.get("brand"),
            image=product.get("image"),
            product_name=product.get("product_name")
        )

    generate_user_products(user, test_products, api_key)

    assert api_key.api_key_products.count() == 4


@pytest.mark.django_db
def test_create_sale_objects_without_conditions(
        create_user,
        create_api_key,
        test_sales,
        test_products,
        create_client_unique_product
):
    user = create_user()

    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )

    for product in test_products:
        create_client_unique_product(
            api_key=api_key,
            nm_id=product.get("nm_id"),
            brand=product.get("brand"),
            image=product.get("image"),
            product_name=product.get("product_name")
        )

    created_product_objs = ClientUniqueProduct.objects.in_bulk(
        [product.get('nm_id') for product in test_products], field_name='nm_id')

    sale_objects_creation_status = create_sale_objects(
        user,
        api_key,
        test_sales,
        [],
        {
            'realizationreport_ids': [],
            'incorrect_reports_data_list': []
        },
        created_product_objs
    )

    assert sale_objects_creation_status
    assert api_key.api_key_sales.count() == 4
    assert api_key.api_key_sales.filter(office_name='Склад WB без названия').exists()


@pytest.mark.django_db
def test_create_sale_objects_with_conditions(
        create_user,
        create_api_key,
        test_sales,
        test_products,
        create_client_unique_product
):
    user = create_user()

    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )

    for product in test_products:
        create_client_unique_product(
            api_key=api_key,
            nm_id=product.get("nm_id"),
            brand=product.get("brand"),
            image=product.get("image"),
            product_name=product.get("product_name")
        )

    created_product_objs = ClientUniqueProduct.objects.in_bulk(
        [product.get('nm_id') for product in test_products], field_name='nm_id')

    sale_objects_creation_status = create_sale_objects(
        user,
        api_key,
        test_sales,
        [27982078],
        {
            'realizationreport_ids': [27982028],
            'incorrect_reports_data_list': []
        },
        created_product_objs
    )

    assert sale_objects_creation_status
    assert api_key.api_key_sales.count() == 2
    assert not api_key.api_key_sales.filter(realizationreport_id__in=[27982078, 27982028]).exists()


def test_get_unique_articles():
    articles_input_data = [
        {"nm_id": 141371096, "brand_name": "Kadiev"},
        {"nm_id": 141371096, "brand_name": "Kadiev"},
        {"nm_id": 141972556, "brand_name": "Kadiev"},
        {"nm_id": 140930947, "brand_name": "Kadiev"},
        {"nm_id": 140930947, "brand_name": "Kadiev"},
        {"nm_id": 140930947, "brand_name": "Kadiev"},
        {"nm_id": 141371096, "brand_name": "Kadiev"},
    ]

    unique_articles = get_unique_articles(articles_input_data)

    expected_articles_output = [
        {"nm_id": 141371096, "brand": "Kadiev"},
        {"nm_id": 141972556, "brand": "Kadiev"},
        {"nm_id": 140930947, "brand": "Kadiev"},
    ]

    assert expected_articles_output == unique_articles


def test_get_unique_reports():
    report_input_data = [
        {"realizationreport_id": 141371096},
        {"realizationreport_id": 141371096},
        {"realizationreport_id": 141972556},
        {"realizationreport_id": 140930947},
        {"realizationreport_id": 140930947},
        {"realizationreport_id": 140930947},
        {"realizationreport_id": 141371096},
    ]

    unique_reports = list(get_unique_reports(report_input_data))
    unique_reports.sort()

    expected_reports_output = [140930947, 141371096, 141972556]

    assert expected_reports_output == unique_reports


@pytest.mark.django_db
def test_generate_reports_without_sales(
        create_user,
        create_api_key
):
    user = create_user()

    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )

    generate_reports(
        user,
        api_key
    )

    assert SaleReport.objects.filter(api_key=api_key).count() == 0


@pytest.mark.django_db
def test_generate_reports_with_sales(
        create_user,
        create_api_key,
        test_sales,
        test_products,
        create_client_unique_product
):
    user = create_user()

    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )
    for product in test_products:
        create_client_unique_product(
            api_key=api_key,
            nm_id=product.get("nm_id"),
            brand=product.get("brand"),
            image=product.get("image"),
            product_name=product.get("product_name")
        )
    created_product_objs = ClientUniqueProduct.objects.in_bulk(
        [product.get('nm_id') for product in test_products], field_name='nm_id')

    create_sale_objects(user, api_key, test_sales, [],
                        {'realizationreport_ids': [], 'incorrect_reports_data_list': []},
                        created_product_objs)

    generate_reports(
        user,
        api_key
    )

    assert SaleReport.objects.filter(api_key=api_key).count() == 4


@pytest.mark.django_db
def test_duplicates_generate_reports(
        create_user,
        create_api_key,
        test_sales,
        test_products,
        create_client_unique_product,
        create_user_report
):
    user = create_user()

    api_key = create_api_key(
        api_key='qweqwesad',
        name='Тест',
        user=user,
        is_current=False,
        is_wb_data_loaded=False,
        is_products_loaded=False,
        is_active_import=False,
        last_reports_update=datetime.now(),
    )
    for product in test_products:
        create_client_unique_product(
            api_key=api_key,
            nm_id=product.get("nm_id"),
            brand=product.get("brand"),
            image=product.get("image"),
            product_name=product.get("product_name")
        )

    created_product_objs = ClientUniqueProduct.objects.in_bulk(
        [product.get('nm_id') for product in test_products], field_name='nm_id')

    create_sale_objects(user, api_key, test_sales, [],
                        {'realizationreport_ids': [], 'incorrect_reports_data_list': []},
                        created_product_objs)

    for i in range(2):
        generate_reports(
            user,
            api_key
        )

    assert SaleReport.objects.filter(api_key=api_key).count() == 4


def test_success_check_sale_obj_validation_without_exception(test_sales):
    success_validation_result = [check_sale_obj_validation(sale) for sale in test_sales]

    assert all(success_validation_result)


def test_success_check_sale_obj_validation_with_exception(test_sales_with_exception):
    success_validation_result = [check_sale_obj_validation(sale) for sale in test_sales_with_exception]

    assert success_validation_result is True


def test_fail_check_sale_obj_validation(test_invalid_sales):
    fail_validation_sales_data = [check_sale_obj_validation(sale) for sale in test_invalid_sales]

    fail_validation_result = []

    for sale, invalid_sale in zip(test_invalid_sales, fail_validation_sales_data):
        if sale.get("realizationreport_id") == invalid_sale.get("realizationreport_id"):
            fail_validation_result.append(True)

    assert all(fail_validation_result)
    assert len(fail_validation_result) == len(test_invalid_sales)









