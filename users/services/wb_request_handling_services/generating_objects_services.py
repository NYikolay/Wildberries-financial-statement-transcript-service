import datetime
import pytz

import numpy as np

from users.models import UnloadedReports, IncorrectReport, SaleReport, ClientUniqueProduct


def get_unloaded_report_object(current_api_key, realizationreport_id):
    return UnloadedReports(api_key=current_api_key, realizationreport_id=realizationreport_id)


def get_incorrect_report_object(current_user, report_data, current_api_key):
    return IncorrectReport(
        api_key=current_api_key,
        owner=current_user,
        realizationreport_id=report_data.realizationreport_id,
        date_from=report_data.date_from,
        date_to=report_data.date_to
    )


def get_unique_product_obj(article_values: dict, api_key):
    product_name = 'Наименование отсутствет на WB' if not article_values.get('title') else article_values.get('title')
    brand_name = f"Бренд отсутствует на WB" if not article_values.get('brand') else article_values.get('brand')

    return ClientUniqueProduct(
        api_key=api_key,
        nm_id=article_values.get('nm_id'),
        brand=brand_name,
        image=article_values.get('img'),
        product_name=product_name
    )


def get_report_object(current_user, api_key, sale, unique_week_uuid):
    return SaleReport(
        api_key=api_key,
        owner=current_user,
        realizationreport_id=sale.realizationreport_id,
        unique_week_uuid=unique_week_uuid,
        year=sale.year,
        week_num=sale.week_num,
        month_num=sale.month_num,
        create_dt=sale.create_dt,
        date_from=sale.date_from,
        date_to=sale.date_to
    )


def get_unloaded_report_object(current_api_key, report_id: int):
    return UnloadedReports(
        api_key=current_api_key,
        realizationreport_id=report_id
    )


def get_sale_object(current_user, sale_obj, api_key, current_product_objs):
    office_name = "Склад WB без названия" if sale_obj.office_name is None else sale_obj.office_name
    brand_name = "Бренд отсутствует на WB" if not sale_obj.brand_name else sale_obj.brand_name
    week_num = datetime.datetime.strptime(sale_obj.date_from, '%Y-%m-%dT%H:%M:%SZ').isocalendar()[1]
    year = datetime.datetime.strptime(sale_obj.date_from, '%Y-%m-%dT%H:%M:%SZ').year
    month_num = datetime.datetime.strptime(sale_obj.date_from, '%Y-%m-%dT%H:%M:%SZ').month
    date_from = datetime.datetime.strptime(
        sale_obj.date_from, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    date_to = datetime.datetime.strptime(
        sale_obj.date_to, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    create_dt = datetime.datetime.strptime(
        sale_obj.create_dt, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    order_dt = datetime.datetime.strptime(
        sale_obj.order_dt, '%Y-%m-%dT%H:%M:%SZ').replace(
        tzinfo=pytz.timezone('Europe/Moscow')) if sale_obj.order_dt else None
    sale_dt = datetime.datetime.strptime(
        sale_obj.sale_dt, '%Y-%m-%dT%H:%M:%SZ').replace(
        tzinfo=pytz.timezone('Europe/Moscow')) if sale_obj.sale_dt else None
    rr_dt = datetime.datetime.strptime(
        sale_obj.rr_dt, '%Y-%m-%dT%H:%M:%SZ').replace(
        tzinfo=pytz.timezone('Europe/Moscow')) if sale_obj.rr_dt else None
    kiz = getattr(sale_obj, 'kiz', None)
    bonus_type_name = getattr(sale_obj, 'bonus_type_name', None)
    product = current_product_objs.get(sale_obj.nm_id).id if current_product_objs.get(sale_obj.nm_id) else np.nan

    return {
        "owner": current_user.id,
        "api_key": api_key.id,
        "week_num": week_num,
        "product": product,
        "year": year,
        "month_num": month_num,
        "realizationreport_id": sale_obj.realizationreport_id,
        "date_from": date_from,
        "date_to": date_to,
        "create_dt": create_dt,
        "gi_id": sale_obj.gi_id,
        "subject_name": sale_obj.subject_name,
        "nm_id": sale_obj.nm_id,
        "brand_name": brand_name,
        "sa_name": sale_obj.sa_name,
        "ts_name": sale_obj.ts_name,
        "barcode": sale_obj.barcode,
        "doc_type_name": sale_obj.doc_type_name,
        "order_dt": order_dt,
        "sale_dt": sale_dt,
        "quantity": sale_obj.quantity,
        "retail_price": sale_obj.retail_price,
        "retail_price_withdisc_rub": sale_obj.retail_price_withdisc_rub,
        "ppvz_for_pay": sale_obj.ppvz_for_pay,
        "penalty": sale_obj.penalty,
        "additional_payment": sale_obj.additional_payment,
        "site_country": sale_obj.site_country,
        "office_name": office_name,
        "srid": sale_obj.srid,
        "delivery_rub": sale_obj.delivery_rub,
        "rid": sale_obj.rid,
        "supplier_oper_name": sale_obj.supplier_oper_name,
        "rrd_id": sale_obj.rrd_id,
        "retail_amount": sale_obj.retail_amount,
        "sale_percent": sale_obj.sale_percent,
        "commission_percent": sale_obj.commission_percent,
        "rr_dt": rr_dt,
        "shk_id": sale_obj.shk_id,
        "delivery_amount": sale_obj.delivery_amount,
        "return_amount": sale_obj.return_amount,
        "gi_box_type_name": sale_obj.gi_box_type_name,
        "product_discount_for_report": sale_obj.product_discount_for_report,
        "supplier_promo": sale_obj.supplier_promo,
        "ppvz_spp_prc": sale_obj.ppvz_spp_prc,
        "ppvz_kvw_prc_base": sale_obj.ppvz_kvw_prc_base,
        "ppvz_kvw_prc": sale_obj.ppvz_kvw_prc,
        "ppvz_sales_commission": sale_obj.ppvz_sales_commission,
        "ppvz_reward": sale_obj.ppvz_reward,
        "acquiring_fee": sale_obj.acquiring_fee,
        "acquiring_bank": sale_obj.acquiring_bank,
        "ppvz_vw": sale_obj.ppvz_vw,
        "ppvz_vw_nds": sale_obj.ppvz_vw_nds,
        "ppvz_office_id": sale_obj.ppvz_office_id,
        "ppvz_office_name": sale_obj.ppvz_office_name,
        "ppvz_supplier_id": sale_obj.ppvz_supplier_id,
        "ppvz_supplier_name": sale_obj.ppvz_supplier_name,
        "ppvz_inn": sale_obj.ppvz_inn,
        "declaration_number": sale_obj.declaration_number,
        "bonus_type_name": bonus_type_name,
        "sticker_id": sale_obj.sticker_id,
        "kiz": kiz,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }
