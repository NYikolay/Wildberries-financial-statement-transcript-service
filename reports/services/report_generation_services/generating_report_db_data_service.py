import json
from typing import List

from django.db.models import (
    Sum, Q, FloatField,
    F, Subquery,
    OuterRef, Value,
    Case, When, Min, Max)
from django.db.models.functions import Coalesce
from users.models import (SaleObject, ClientUniqueProduct, NetCost, SaleReport, TaxRate)

from reports.services.report_generation_services.generating_sum_aggregation_objs_service import get_aggregate_sum_dicts


def get_report_db_inter_data(
        current_user,
        current_api_key,
        filter_period_conditions
):
    """
    The function is responsible for sending queries to the database to obtain information for the report
    :param current_user: Current authorized user
    :param current_api_key: The user's current active WBApiKey
    :param filter_period_conditions: Formed an instance of the Q() class to filter data
    :return: Returns a dictionary containing data from the Reporting Database
    """
    general_dict_aggregation_objs: dict = get_aggregate_sum_dicts()
    sum_aggregation_objs_dict: dict = general_dict_aggregation_objs.get('sum_aggregation_objs_dict')
    net_costs_sum_aggregations_objs: dict = general_dict_aggregation_objs.get('net_costs_sum_aggregation_objs')
    tax_rates_sum_aggregation_objs: dict = general_dict_aggregation_objs.get('tax_rates_sum_aggregation_objs')

    tax_rates_objects = TaxRate.objects.filter(
        api_key=current_api_key
    ).order_by('-commencement_date').only('tax_rate', 'commencement_date')

    tax_rates_case_dict: list = [
        When(
            sale_dt__gte=obj.commencement_date, then=Value(obj.tax_rate)
        ) for obj in tax_rates_objects
    ]

    sale_objects_by_weeks = SaleObject.objects.filter(
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

    supplier_costs_sum_list = SaleReport.objects.filter(
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

    wb_costs_sum_list = SaleReport.objects.filter(
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
    ).order_by('date_from').values('year', 'week_num').annotate(
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
        total_wb_costs_sum=
        Sum(
            Coalesce(F('storage_cost'), 0, output_field=FloatField()) +
            Coalesce(F('cost_paid_acceptance'), 0, output_field=FloatField()) +
            Coalesce(F('other_deductions'), 0, output_field=FloatField())
        )
    )

    sale_objects_by_products = SaleObject.objects.filter(
        filter_period_conditions,
        owner=current_user,
        api_key=current_api_key,
        nm_id__isnull=False
    ).annotate(
        net_cost=Subquery(
            NetCost.objects.filter(
                product=OuterRef('product'),
                cost_date__lte=OuterRef('order_dt')
            ).order_by('-cost_date').values('amount')[:1]
        ),
    ).order_by('brand_name', 'nm_id').values('nm_id').annotate(
        **sum_aggregation_objs_dict,
        **net_costs_sum_aggregations_objs,
        image=F('product__image'),
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

    is_empty_reports_values = SaleReport.objects.filter(
        filter_period_conditions,
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
        'sale_objects_by_weeks': sale_objects_by_weeks,
        'supplier_costs_sum_list': supplier_costs_sum_list,
        'wb_costs_sum_list': wb_costs_sum_list,
        'sale_objects_by_products': sale_objects_by_products,
        'is_empty_reports_values': is_empty_reports_values,
        'is_empty_netcosts_values': is_empty_netcosts_values,
        'is_exists_tax_values': is_exists_tax_values
    }
