from django.db.models import (
    Sum, Q, FloatField,
    F, Subquery,
    OuterRef, Value,
    Case, When, Min, Max, QuerySet, Count)
from django.db.models.functions import Coalesce
from django.db import connection

from users.models import (SaleObject, ClientUniqueProduct, NetCost, SaleReport, TaxRate)


def get_calculated_financials_by_products(
        current_user,
        current_api_key,
        filter_period_conditions,
        sum_aggregation_objs_dict,
        net_costs_sum_aggregations_objs,
        total_revenue,
        total_products_count,
        annotations_objs
) -> QuerySet:
    """
    The function is needed to send a query to the database for the
    SaleObject model and calculate a financial report for each unique product of a particular user
    :param current_user: request.user
    :param current_api_key: active WebAPIKey of request.user
    :param filter_period_conditions: Dictionary containing Q() objects in the value to filter values from the database:
    1. period
    2. subject_name
    3. brand_name
    :param sum_aggregation_objs_dict: Dictionary containing Coalesce(Sum()) objects
    in the value to filter values from the database
    :param net_costs_sum_aggregations_objs: ictionary containing Coalesce(Sum()) objects in
    the value to filter values from the database
    :param total_revenue: Total revenue generated by
    reports.services.report_generation_services.get_total_financials_service.get_total_financials()
    :param total_products_count: Number of items received from SaleObject() model objects as a result of
    reports.services.report_generation_services.generating_report_db_data_service.get_report_db_inter_data
    :param annotations_objs: A dictionary containing objects for calculating values when annotating a query to the
    SaleObject model. Result of
    reports.services.report_generation_services.generating_sum_aggregation_objs_service.get_financials_annotation_objects
    :return: QuerySet containing the calculated financial report for each unique item of a particular user.
    """

    calculated_financials = SaleObject.objects.filter(
        ~Q(nm_id=99866376),
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
        nm_id__isnull=False,
    ).annotate(
        net_cost=Subquery(
            NetCost.objects.filter(
                product=OuterRef('product'),
                cost_date__lte=OuterRef('order_dt')
            ).order_by('-cost_date').values('amount')[:1]
        ),
    ).order_by('barcode').values('barcode').annotate(
        **sum_aggregation_objs_dict,
        **net_costs_sum_aggregations_objs,
        image=Min('product__image'),
        product_name=Min('product__product_name'),
        logistic_sum=(
                Coalesce(Sum(
                    'delivery_rub',
                    filter=~Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField()) -
                Coalesce(Sum(
                    'delivery_rub',
                    filter=Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField())
        ),
        penalty_sum=Coalesce(Sum('penalty'), 0, output_field=FloatField()),
        additional_payment_sum=Coalesce(Sum('additional_payment'), 0, output_field=FloatField()),
        total_revenue=Value(total_revenue, output_field=FloatField()),
        total_products_count=Value(total_products_count, output_field=FloatField()),
        **annotations_objs,
    ).values('nm_id', 'barcode', 'image', 'product_name',
             'revenue_by_article', 'share_in_revenue',
             'product_marginality', 'share_in_number')

    return calculated_financials


def get_nm_ids_revenues_by_weeks(
        current_user,
        current_api_key,
        current_barcodes,
        sum_aggregation_objs_dict,
        filter_period_conditions,
        annotations_objs) -> QuerySet:
    """
    The function sends a query to the database to calculate the XYZ analysis.
    WARNING, the filtering by weeks for the last 12 months is used.
    :param current_user: request.user
    :param current_api_key: active WebAPIKey of request.user
    :param current_barcodes: A list containing the unique barcode by nm_id of the current user from the SaleObject table
    :param sum_aggregation_objs_dict: Dictionary containing Coalesce(Sum()) objects
    in the value to filter values from the database
    :param filter_period_conditions: The result of the function get_past_months_filters , contains objects
    Q(year=... | week_num__in=....) for the LAST 12 MONTHS (Always, regardless of user filters)
    :param annotations_objs: A dictionary containing objects for calculating values when annotating a query to the
    SaleObject model. Result of
    reports.services.report_generation_services.generating_sum_aggregation_objs_service.get_financials_annotation_objects
    :return: Returns the calculated revenue values on a weekly basis for each unique nm_id from current_nm_ids_set
    """

    revenues_queryset = SaleObject.objects.filter(
        ~Q(nm_id=99866376),
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
        barcode__in=current_barcodes,
    ).order_by('week_num').values('week_num', 'year').annotate(
        **sum_aggregation_objs_dict,
        revenue_by_article=annotations_objs.get('revenue_by_article')
    ).order_by('-barcode').values('barcode', 'nm_id', 'year', 'week_num', 'revenue_by_article')

    return revenues_queryset


def get_sale_objects_by_barcode_by_weeks(
        current_user,
        current_api_key,
        filter_period_conditions,
        sum_aggregation_objs_dict,
        net_costs_sum_aggregations_objs,
        barcode,
        nm_id
):
    sale_objects_by_barcode_by_weeks = SaleObject.objects.filter(
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
        barcode=barcode,
        nm_id=nm_id
    ).annotate(
        net_cost=Subquery(
            NetCost.objects.filter(
                product=OuterRef('product'),
                cost_date__lte=OuterRef('order_dt')
            ).order_by('-cost_date').values('amount')[:1]
        ),
    ).order_by('date_from').values('year', 'week_num').annotate(
        **sum_aggregation_objs_dict,
        **net_costs_sum_aggregations_objs,
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
        logistic_sum=(
                Coalesce(Sum(
                    'delivery_rub',
                    filter=~Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField()) -
                Coalesce(Sum(
                    'delivery_rub',
                    filter=Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField())
        ),
        penalty_sum=Coalesce(Sum('penalty'), 0, output_field=FloatField()),
        additional_payment_sum=Coalesce(Sum('additional_payment'), 0, output_field=FloatField())
    )
    return sale_objects_by_barcode_by_weeks


def get_sale_objects_by_weeks(
        current_user,
        current_api_key,
        filter_period_conditions,
        sum_aggregation_objs_dict,
        tax_rates_sum_aggregation_objs,
        net_costs_sum_aggregations_objs
):
    tax_rates_objects = TaxRate.objects.filter(
        api_key=current_api_key
    ).order_by('-commencement_date').only('tax_rate', 'commencement_date')

    tax_rates_case_dict: list = [
        When(
            sale_dt__gte=obj.commencement_date, then=Value(obj.tax_rate)
        ) for obj in tax_rates_objects
    ]

    sale_objects = SaleObject.objects.filter(
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
    ).annotate(
        price_including_tax=(
                (F('retail_amount') *
                 Case(*tax_rates_case_dict, default=Value(0), output_field=FloatField())) / 100
        ),
        net_cost=Subquery(
            NetCost.objects.filter(
                product=OuterRef('product'),
                cost_date__lte=OuterRef('order_dt')
            ).order_by('-cost_date').values('amount')[:1]
        ),
    ).order_by('date_from').values('year', 'week_num').annotate(
        **sum_aggregation_objs_dict,
        **tax_rates_sum_aggregation_objs,
        **net_costs_sum_aggregations_objs,
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
        logistic_sum=(
                Coalesce(Sum(
                    'delivery_rub',
                    filter=~Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField()) -
                Coalesce(Sum(
                    'delivery_rub',
                    filter=Q(supplier_oper_name__icontains='Логистика сторно')), 0, output_field=FloatField())
        ),
        penalty_sum=Coalesce(Sum('penalty'), 0, output_field=FloatField()),
        additional_payment_sum=Coalesce(Sum('additional_payment'), 0, output_field=FloatField())
    )

    return sale_objects


def get_empty_db_values(
        current_user,
        current_api_key,
        period_q_objs
):
    is_empty_reports_values = SaleReport.objects.filter(
        period_q_objs,
        Q(storage_cost__isnull=True) |
        Q(cost_paid_acceptance__isnull=True) |
        Q(other_deductions__isnull=True) |
        Q(supplier_costs__isnull=True),
        owner=current_user,
        api_key=current_api_key,
        ).exists()

    is_empty_netcosts_values = ClientUniqueProduct.objects.filter(
        api_key=current_api_key,
        cost_prices__isnull=True
    ).exists()

    is_exists_tax_values = TaxRate.objects.filter(
        api_key=current_api_key
    ).exists()

    return {
        'is_empty_reports_values': is_empty_reports_values,
        'is_empty_netcosts_values': is_empty_netcosts_values,
        'is_exists_tax_values': is_exists_tax_values,
    }


def get_products_count_by_period(current_user, current_api_key, filter_period_conditions):
    products_count_by_period = SaleObject.objects.filter(
        ~Q(nm_id=99866376),
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
        nm_id__isnull=False
    ).order_by('barcode').values('barcode').annotate(count=Count('id')).count()

    return products_count_by_period


def get_supplier_costs_sum(current_user, current_api_key, filter_period_conditions):
    supplier_costs_sum = SaleReport.objects.filter(
        id__in=Subquery(
            SaleReport.objects.filter(
                filter_period_conditions,
                owner=current_user,
                api_key=current_api_key,
            ).distinct('create_dt').values_list('id', flat=True)
        )).order_by('date_from').values('year', 'week_num').annotate(
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
        supplier_costs_sum=Coalesce(Sum('supplier_costs'), 0, output_field=FloatField())
    )

    return supplier_costs_sum


def get_wb_costs_sum(current_user, current_api_key, filter_period_conditions):
    wb_costs_sum = SaleReport.objects.filter(
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
    ).order_by('date_from').values('year', 'week_num').annotate(
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
        total_wb_costs_sum=Sum(
            Coalesce(F('storage_cost'), 0, output_field=FloatField()) +
            Coalesce(F('cost_paid_acceptance'), 0, output_field=FloatField()) +
            Coalesce(F('other_deductions'), 0, output_field=FloatField())
        )
    )

    return wb_costs_sum


def get_report_db_inter_data(
        current_user,
        current_api_key,
        filter_period_conditions: dict,
        general_dict_aggregation_objs: dict
):
    """
    The function is responsible for sending queries to the database to obtain information for the report
    :param current_user: Current authorized user
    :param current_api_key: The user's current active WBApiKey
    :param filter_period_conditions: Formed an instance of the Q() class to filter data
    :param general_dict_aggregation_objs: ...
    :return: Returns a dictionary containing data from the Reporting Database
    """
    sum_aggregation_objs_dict: dict = general_dict_aggregation_objs.get('sum_aggregation_objs_dict')
    net_costs_sum_aggregations_objs: dict = general_dict_aggregation_objs.get('net_costs_sum_aggregation_objs')
    tax_rates_sum_aggregation_objs: dict = general_dict_aggregation_objs.get('tax_rates_sum_aggregation_objs')

    with connection.cursor() as cursor:
        sql = "SET JIT = OFF;"
        cursor.execute(sql)

    sale_objects_by_weeks = get_sale_objects_by_weeks(
        current_user,
        current_api_key,
        filter_period_conditions,
        sum_aggregation_objs_dict,
        tax_rates_sum_aggregation_objs,
        net_costs_sum_aggregations_objs
    )

    products_count_by_period = get_products_count_by_period(
        current_user,
        current_api_key,
        filter_period_conditions
    )

    supplier_costs_sum_list = get_supplier_costs_sum(
        current_user,
        current_api_key,
        filter_period_conditions
    )

    wb_costs_sum_list = get_wb_costs_sum(
        current_user,
        current_api_key,
        filter_period_conditions
    )

    empty_user_data_statuses_dict = get_empty_db_values(
        current_user,
        current_api_key,
        filter_period_conditions
    )

    return {
        'sale_objects_by_weeks': sale_objects_by_weeks,
        'supplier_costs_sum_list': supplier_costs_sum_list,
        'wb_costs_sum_list': wb_costs_sum_list,
        'is_empty_reports_values': empty_user_data_statuses_dict.get('is_empty_reports_values'),
        'is_empty_netcosts_values': empty_user_data_statuses_dict.get('is_empty_netcosts_values'),
        'is_exists_tax_values': empty_user_data_statuses_dict.get('is_exists_tax_values'),
        'products_count_by_period': products_count_by_period,
    }
