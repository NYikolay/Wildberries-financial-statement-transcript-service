from datetime import datetime
import pytz

from users.models import SaleObject


def handle_sale_obj(current_user, sale_obj: dict, api_key, current_product_objs):
    """
    The function generates an instance of the SaleObject class.
    IMPORTANT: Such values as: date_from, date_to, create_dt, order_dt, sale_dt
    do not check for None, because they are pre-checked by get_incorrect_reports_lst function
    :param current_user:
    :param sale_obj: Dictionary containing sales data
    :param api_key: WBApiKey object of the current user
    :param current_product_objs:
    :return:
    """
    wb_office_name = sale_obj.get('office_name')
    office_name = 'Склад WB без названия' if wb_office_name is None else wb_office_name
    brand_name = f"Бренд отсутствует на WB" if not sale_obj.get('brand_name') else sale_obj.get('brand_name')
    week_num = datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').isocalendar()[1]
    year = datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').year
    month_num = datetime.strptime(sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').month
    date_from = datetime.strptime(
        sale_obj.get('date_from'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    date_to = datetime.strptime(
        sale_obj.get('date_to'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    create_dt = datetime.strptime(
        sale_obj.get('create_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    order_dt = datetime.strptime(
        sale_obj.get('order_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    sale_dt = datetime.strptime(
        sale_obj.get('sale_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))
    rr_dt = None if not sale_obj.get('rr_dt') else datetime.strptime(
        sale_obj.get('rr_dt'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.timezone('Europe/Moscow'))

    return SaleObject(
        owner=current_user,
        api_key=api_key,
        week_num=week_num,
        product=current_product_objs.get(sale_obj.get('nm_id')),
        year=year,
        month_num=month_num,
        realizationreport_id=sale_obj.get('realizationreport_id'),
        date_from=date_from,
        date_to=date_to,
        create_dt=create_dt,
        gi_id=sale_obj.get('gi_id'),
        subject_name=sale_obj.get('subject_name'),
        nm_id=sale_obj.get('nm_id'),
        brand_name=brand_name,
        sa_name=sale_obj.get('sa_name'),
        ts_name=sale_obj.get('ts_name'),
        barcode=sale_obj.get('barcode'),
        doc_type_name=sale_obj.get('doc_type_name'),
        order_dt=order_dt,
        sale_dt=sale_dt,
        quantity=sale_obj.get('quantity'),
        retail_price=sale_obj.get('retail_price'),
        retail_price_withdisc_rub=sale_obj.get('retail_price_withdisc_rub'),
        ppvz_for_pay=sale_obj.get('ppvz_for_pay'),
        penalty=sale_obj.get('penalty'),
        additional_payment=sale_obj.get('additional_payment'),
        site_country=sale_obj.get('site_country'),
        office_name=office_name,
        srid=sale_obj.get('srid'),
        delivery_rub=sale_obj.get('delivery_rub'),
        rid=sale_obj.get('rid'),
        supplier_oper_name=sale_obj.get('supplier_oper_name'),
        rrd_id=sale_obj.get('rrd_id'),
        retail_amount=sale_obj.get('retail_amount'),
        sale_percent=sale_obj.get('sale_percent'),
        commission_percent=sale_obj.get('commission_percent'),
        rr_dt=rr_dt,
        shk_id=sale_obj.get('shk_id'),
        delivery_amount=sale_obj.get('delivery_amount'),
        return_amount=sale_obj.get('return_amount'),
        gi_box_type_name=sale_obj.get('gi_box_type_name'),
        product_discount_for_report=sale_obj.get('product_discount_for_report'),
        supplier_promo=sale_obj.get('supplier_promo'),
        ppvz_spp_prc=sale_obj.get('ppvz_spp_prc'),
        ppvz_kvw_prc_base=sale_obj.get('ppvz_kvw_prc_base'),
        ppvz_kvw_prc=sale_obj.get('ppvz_kvw_prc'),
        ppvz_sales_commission=sale_obj.get('ppvz_sales_commission'),
        ppvz_reward=sale_obj.get('ppvz_reward'),
        acquiring_fee=sale_obj.get('acquiring_fee'),
        acquiring_bank=sale_obj.get('acquiring_bank'),
        ppvz_vw=sale_obj.get('ppvz_vw'),
        ppvz_vw_nds=sale_obj.get('ppvz_vw_nds'),
        ppvz_office_id=sale_obj.get('ppvz_office_id'),
        ppvz_office_name=sale_obj.get('ppvz_office_name'),
        ppvz_supplier_id=sale_obj.get('ppvz_supplier_id'),
        ppvz_supplier_name=sale_obj.get('ppvz_supplier_name'),
        ppvz_inn=sale_obj.get('ppvz_inn'),
        declaration_number=sale_obj.get('declaration_number'),
        bonus_type_name=sale_obj.get('bonus_type_name'),
        sticker_id=sale_obj.get('sticker_id'),
        kiz=sale_obj.get('kiz')
    )


def create_sale_objects(
        current_user,
        current_api_key,
        sales,
        generated_reports_ids,
        incorrect_reports_ids,
        generated_products_objs
):
    sale_objects_list: list = []

    for sale in sales:
        if sale.get('realizationreport_id') in generated_reports_ids \
                or sale.get('realizationreport_id') in incorrect_reports_ids.get('realizationreport_ids'):
            continue
        sale_objects_list.append(handle_sale_obj(current_user, sale, current_api_key, generated_products_objs))

    if len(sale_objects_list) == 0:
        return {
            'status': False,
            'message': 'На Wildberries отсутствуют новые корректные отчёты за текущую дату.'
        }

    SaleObject.objects.bulk_create(sale_objects_list, batch_size=5000)

    return {'status': True}
