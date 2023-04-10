import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Subquery, Min, Max, F, Value, CharField, JSONField, ExpressionWrapper
from django.db.models.functions import Concat
from django.contrib.postgres.aggregates import ArrayAgg
from users.models import SaleReport, SaleObject


def get_filters_db_data(current_api_key):
    filter_period_queryset = SaleObject.objects.filter(
        api_key=current_api_key
    ).order_by('-date_from').values('year', 'week_num').annotate(
        date_to=Max('date_to'),
        date_from=Min('date_from'),
        subject_names=ArrayAgg(
            'subject_name',
            distinct=True,
        ),
        brand_names=ArrayAgg(
            'brand_name',
            distinct=True
        )
    ).values('year', 'week_num', 'date_from', 'date_to', 'subject_names', 'brand_names')

    filter_categories_queryset = SaleObject.objects.filter(
        api_key=current_api_key
    ).order_by('subject_name').values('subject_name').annotate(
        week_nums=ArrayAgg(
            Concat('week_num', Value(':'), 'year', output_field=CharField()),
            distinct=True
        ),
        brand_names=ArrayAgg(
            'brand_name',
            distinct=True
        )
    ).values('subject_name', 'week_nums', 'brand_names')

    filter_brands_queryset = SaleObject.objects.filter(
        api_key=current_api_key
    ).order_by('brand_name').values('brand_name').annotate(
        week_nums=ArrayAgg(
            Concat('week_num', Value(':'), 'year', output_field=CharField()),
            distinct=True
        ),
        subject_names=ArrayAgg(
            'subject_name',
            distinct=True
        )
    ).values('brand_name', 'week_nums', 'subject_names')

    return {
        'filter_period_queryset': filter_period_queryset,
        'filter_categories': filter_categories_queryset,
        'filter_brands': filter_brands_queryset,
    }
