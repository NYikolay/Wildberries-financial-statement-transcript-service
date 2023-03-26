from datetime import datetime
from typing import List
import pytest

from payments.models import SubscriptionTypes, SubscriptionType
from users.models import User, UserDiscount, UserSubscription, WBApiKey, IncorrectReport, ClientUniqueProduct, \
    SaleReport


@pytest.fixture
def test_password():
    return 'test123123qwe123'


@pytest.fixture
def test_subscriptions_data() -> List[tuple]:

    subscriptions_data: List[tuple] = [
        (SubscriptionTypes.TEST, 1, 'Неделя', 0, 0),
        (SubscriptionTypes.START, 1, 'Месяц', 4400, 0),
        (SubscriptionTypes.MIDDLE, 3, 'Месяца', 13200, 10),
        (SubscriptionTypes.LONG, 6, 'Месяцев', 26400, 20)
    ]

    return subscriptions_data


@pytest.fixture
def test_incorrect_reports():
    incorrect_reports = [
        {"realizationreport_id": 28856935, "date_from": datetime.now(), "date_to": datetime.now()},
        {"realizationreport_id": 28856936, "date_from": datetime.now(), "date_to": datetime.now()},
        {"realizationreport_id": 27905885, "date_from": datetime.now(), "date_to": datetime.now()}
    ]

    return incorrect_reports


@pytest.fixture
def test_products():
    unique_articles = [{
        "nm_id": 141371096,
        "brand": "Hanes Store",
        "image": "https://basket-10.wb.ru/vol1413/part141371/141371096/images/tm/1.jpg",
        "product_name": "Носки женские короткие набор белые черные хлопок"
    }, {
        "nm_id": 141972556,
        "brand": "Hanes Store",
        "image": "https://basket-10.wb.ru/vol1419/part141972/141972556/images/tm/1.jpg",
        "product_name": "Носки женские короткие набор белые черные хлопок"
    }, {
        "nm_id": 140930947,
        "brand": "Hanes Store",
        "image": "https://basket-10.wb.ru/vol1409/part140930/140930947/images/tm/1.jpg",
        "product_name": "Носки женские короткие белые 1 пара"
    }, {
        "nm_id": 141370942,
        "brand": "Hanes Store",
        "image": "https://basket-10.wb.ru/vol1413/part141370/141370942/images/tm/1.jpg",
        "product_name": "Носки женские короткие набор белые черные хлопок"
    }]

    return unique_articles


@pytest.fixture
def test_sales():
    sales = [
        {
            "realizationreport_id": 27982018,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": 11597805863,
            "gi_id": 7997454,
            "subject_name": "Ботинки",
            "nm_id": 141371096,
            "brand_name": "Kadiev",
            "sa_name": "К-5023/17К-5023/17",
            "ts_name": "39",
            "barcode": "2036379766665",
            "doc_type_name": "Продажа",
            "quantity": 1,
            "retail_price": 7500,
            "retail_amount": 4150,
            "sale_percent": 30,
            "commission_percent": 0.23,
            "office_name": "Коледино",
            "supplier_oper_name": "Продажа",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": "2023-03-12T00:00:00Z",
            "shk_id": 6483881955,
            "retail_price_withdisc_rub": 5250,
            "delivery_amount": 0,
            "return_amount": 0,
            "delivery_rub": 0,
            "gi_box_type_name": "Без коробов",
            "product_discount_for_report": 30,
            "supplier_promo": 0,
            "rid": 0,
            "ppvz_spp_prc": 0.1746,
            "ppvz_kvw_prc_base": 0.1917,
            "ppvz_kvw_prc": 0.0171,
            "ppvz_sales_commission": 89.58,
            "ppvz_for_pay": 4084.84,
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
            "site_country": "RU",
            "penalty": 0,
            "additional_payment": 0,
            "srid": "36143466073767957.0.0"
        },
        {
            "realizationreport_id": 27982078,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": 11597805864,
            "gi_id": 7997454,
            "subject_name": "Ботинки",
            "nm_id": 141972556,
            "brand_name": "Kadiev",
            "sa_name": "К-5023/17К-5023/17",
            "ts_name": "39",
            "barcode": "2036379766665",
            "doc_type_name": "Продажа",
            "quantity": 0,
            "retail_price": 0,
            "retail_amount": 0,
            "sale_percent": 0,
            "commission_percent": 0,
            "office_name": "Коледино",
            "supplier_oper_name": "Логистика",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": "2023-03-12T00:00:00Z",
            "shk_id": 6483881955,
            "retail_price_withdisc_rub": 0,
            "delivery_amount": 1,
            "return_amount": 0,
            "delivery_rub": 127.36,
            "gi_box_type_name": "Микс",
            "product_discount_for_report": 0,
            "supplier_promo": 0,
            "rid": 0,
            "ppvz_spp_prc": 0,
            "ppvz_kvw_prc_base": 0,
            "ppvz_kvw_prc": 0,
            "ppvz_sales_commission": 0,
            "ppvz_for_pay": 0,
            "ppvz_reward": 0,
            "acquiring_fee": 0,
            "acquiring_bank": "",
            "ppvz_vw": 0,
            "ppvz_vw_nds": 0,
            "ppvz_office_id": 202886,
            "ppvz_supplier_id": 369039,
            "ppvz_supplier_name": "ООО \"СОЮЗ\"",
            "ppvz_inn": "2511117161",
            "declaration_number": "",
            "bonus_type_name": "К клиенту при продаже",
            "sticker_id": "",
            "site_country": "RU",
            "penalty": 0,
            "additional_payment": 0,
            "srid": "36143466073767957.0.0"
        },
        {
            "realizationreport_id": 27982028,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": 11597805865,
            "gi_id": 7997454,
            "subject_name": "Ботинки",
            "nm_id": 140930947,
            "brand_name": "Kadiev",
            "sa_name": "К-5023/17К-5023/17",
            "ts_name": "41",
            "barcode": "2036379766689",
            "doc_type_name": "Продажа",
            "quantity": 0,
            "retail_price": 0,
            "retail_amount": 0,
            "sale_percent": 0,
            "commission_percent": 0,
            "office_name": "Новосибирск",
            "supplier_oper_name": "Логистика",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": "2023-03-12T00:00:00Z",
            "shk_id": 6486075287,
            "retail_price_withdisc_rub": 0,
            "delivery_amount": 1,
            "return_amount": 0,
            "delivery_rub": 127.36,
            "gi_box_type_name": "Микс",
            "product_discount_for_report": 0,
            "supplier_promo": 0,
            "rid": 0,
            "ppvz_spp_prc": 0,
            "ppvz_kvw_prc_base": 0,
            "ppvz_kvw_prc": 0,
            "ppvz_sales_commission": 0,
            "ppvz_for_pay": 0,
            "ppvz_reward": 0,
            "acquiring_fee": 0,
            "acquiring_bank": "",
            "ppvz_vw": 0,
            "ppvz_vw_nds": 0,
            "ppvz_office_id": 202886,
            "ppvz_supplier_id": 369039,
            "ppvz_supplier_name": "ООО \"СОЮЗ\"",
            "ppvz_inn": "2511117161",
            "declaration_number": "",
            "bonus_type_name": "К клиенту при продаже",
            "sticker_id": "",
            "site_country": "RU",
            "penalty": 0,
            "additional_payment": 0,
            "srid": "36143466073767957.2.0"
        },
        {
            "realizationreport_id": 27982048,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": 11597805866,
            "gi_id": 7997454,
            "subject_name": "Ботинки",
            "nm_id": 141370942,
            "brand_name": "Kadiev",
            "sa_name": "К-5023/17К-5023/17",
            "ts_name": "41",
            "barcode": "2036379766689",
            "doc_type_name": "Продажа",
            "quantity": 1,
            "retail_price": 7500,
            "retail_amount": 4007,
            "sale_percent": 30,
            "commission_percent": 0.23,
            "office_name": None,
            "supplier_oper_name": "Продажа",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": "2023-03-12T00:00:00Z",
            "shk_id": 6486075287,
            "retail_price_withdisc_rub": 5250,
            "delivery_amount": 0,
            "return_amount": 0,
            "delivery_rub": 0,
            "gi_box_type_name": "Без коробов",
            "product_discount_for_report": 30,
            "supplier_promo": 0,
            "rid": 0,
            "ppvz_spp_prc": 0.1973,
            "ppvz_kvw_prc_base": 0.1917,
            "ppvz_kvw_prc": -0.0056,
            "ppvz_sales_commission": -29.58,
            "ppvz_for_pay": 4083.37,
            "ppvz_reward": 170.3,
            "acquiring_fee": 34.06,
            "acquiring_bank": "Сбербанк Росси 7707083893",
            "ppvz_vw": -233.94,
            "ppvz_vw_nds": -46.79,
            "ppvz_office_id": 202886,
            "ppvz_supplier_id": 369039,
            "ppvz_supplier_name": "ООО \"СОЮЗ\"",
            "ppvz_inn": "2511117161",
            "declaration_number": "",
            "sticker_id": "",
            "site_country": "RU",
            "penalty": 0,
            "additional_payment": 0,
            "srid": "36143466073767957.2.0"
        },
    ]

    return sales


@pytest.fixture
def test_sales_with_exception():
    sales = [{
            "realizationreport_id": 27982018,
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
            "quantity": 0,
            "retail_price": 7500,
            "retail_amount": 4150,
            "sale_percent": 30,
            "commission_percent": 0.23,
            "office_name": "Коледино",
            "supplier_oper_name": "Логистика",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": "2023-03-12T00:00:00Z",
            "shk_id": 6483881955,
            "retail_price_withdisc_rub": 0,
            "delivery_amount": 0,
            "return_amount": 0,
            "delivery_rub": 0,
            "gi_box_type_name": "Без коробов",
            "product_discount_for_report": 30,
            "supplier_promo": 0,
            "rid": 0,
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
            "site_country": "RU",
            "penalty": 0,
            "additional_payment": 0,
            "srid": "36143466073767957.0.0"
        }]

    return sales


@pytest.fixture
def test_invalid_sales():
    sales = [
        {
            "realizationreport_id": 27982018,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": 11597805863,
            "gi_id": 7997454,
            "subject_name": "Ботинки",
            "nm_id": 141371096,
            "brand_name": "Kadiev",
            "sa_name": "К-5023/17К-5023/17",
            "ts_name": "39",
            "barcode": "2036379766665",
            "doc_type_name": "Продажа",
            "quantity": 1,
            "retail_price": 7500,
            "retail_amount": None,
            "sale_percent": 30,
            "commission_percent": 0.23,
            "office_name": "Коледино",
            "supplier_oper_name": "Продажа",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": "2023-03-12T00:00:00Z",
            "shk_id": 6483881955,
            "retail_price_withdisc_rub": 5250,
            "delivery_amount": None,
            "return_amount": 0,
            "delivery_rub": 0,
            "gi_box_type_name": "Без коробов",
            "product_discount_for_report": 30,
            "supplier_promo": 0,
            "rid": 0,
            "ppvz_spp_prc": 0.1746,
            "ppvz_kvw_prc_base": 0.1917,
            "ppvz_kvw_prc": 0.0171,
            "ppvz_sales_commission": 89.58,
            "ppvz_for_pay": 4084.84,
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
            "site_country": "RU",
            "penalty": 0,
            "additional_payment": 0,
            "srid": "36143466073767957.0.0"
        },
        {
            "realizationreport_id": 27982018,
            "date_from": "2023-03-06T00:00:00Z",
            "date_to": "2023-03-12T00:00:00Z",
            "create_dt": "2023-03-13T05:51:14Z",
            "suppliercontract_code": None,
            "rrd_id": 11597805863,
            "gi_id": 7997454,
            "subject_name": "Ботинки",
            "nm_id": 141371096,
            "brand_name": None,
            "sa_name": "К-5023/17К-5023/17",
            "ts_name": "39",
            "barcode": "2036379766665",
            "doc_type_name": "Продажа",
            "quantity": 1,
            "retail_price": None,
            "retail_amount": 123,
            "sale_percent": 30,
            "commission_percent": 0.23,
            "office_name": "Коледино",
            "supplier_oper_name": "Продажа",
            "order_dt": "2023-02-28T00:00:00Z",
            "sale_dt": "2023-03-12T00:00:00Z",
            "rr_dt": "2023-03-12T00:00:00Z",
            "shk_id": 6483881955,
            "retail_price_withdisc_rub": 5250,
            "delivery_amount": 123,
            "return_amount": 0,
            "delivery_rub": 0,
            "gi_box_type_name": "Без коробов",
            "product_discount_for_report": 30,
            "supplier_promo": 0,
            "rid": 0,
            "ppvz_spp_prc": 0.1746,
            "ppvz_kvw_prc_base": 0.1917,
            "ppvz_kvw_prc": 0.0171,
            "ppvz_sales_commission": 89.58,
            "ppvz_for_pay": 4084.84,
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
            "site_country": "RU",
            "penalty": 0,
            "additional_payment": 0,
            "srid": "36143466073767957.0.0"
        },

    ]

    return sales


@pytest.fixture
def create_user(db, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        kwargs['is_accepted_terms_of_offer'] = True
        kwargs['is_active'] = True
        if 'email' not in kwargs:
            kwargs['email'] = 'commery_123test@mail.ru'
        return User.objects.create(**kwargs)
    return make_user


@pytest.fixture()
def create_api_key(db):
    def make_api_key(**kwargs):
        return WBApiKey.objects.create(**kwargs)
    return make_api_key


@pytest.fixture
def create_subscription_types(db, test_subscriptions_data) -> list:
    def make_subscription_type(**kwargs):
        return SubscriptionType.objects.create(**kwargs)

    subscriptions_data: List[tuple] = test_subscriptions_data
    final_subs_data: list = []

    for subscription_type, duration, duration_desc, cost, discount in subscriptions_data:
        final_subs_data.append(make_subscription_type(
            type=subscription_type,
            duration=duration,
            duration_desc=duration_desc,
            cost=cost,
            build_in_discount=discount
        ))

    return final_subs_data


@pytest.fixture
def create_user_discount(db):
    def make_user_discount(**kwargs):
        return UserDiscount.objects.create(**kwargs, is_active=True)
    return make_user_discount


@pytest.fixture
def create_user_subscription(db):
    def make_user_subscription(**kwargs):
        return UserSubscription.objects.create(**kwargs)
    return make_user_subscription


@pytest.fixture
def create_incorrect_reports(db):
    def make_incorrect_reports(**kwargs):
        return IncorrectReport.objects.create(**kwargs)

    return make_incorrect_reports


@pytest.fixture
def create_client_unique_product(db):
    def make_client_unique_product(**kwargs):
        return ClientUniqueProduct.objects.create(**kwargs)

    return make_client_unique_product


@pytest.fixture
def create_user_report(db):
    def make_user_report(**kwargs):
        return SaleReport.objects.create(**kwargs)

    return make_user_report
