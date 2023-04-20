from typing import List, Union

from django.db.models import QuerySet
from django.db.models import Subquery, Min, Max, F
from users.models import SaleReport


def get_filters_db_data(current_api_key) -> dict:
    """
    The function is used to generate a list consisting of unique weeks by year ( disctinct by create_dt )
    :param current_api_key: active WebAPIKey of request.user
    :return: list consisting of unique weeks by year
    """
    filter_period_queryset: Union[QuerySet, List[dict]] = SaleReport.objects.filter(
        id__in=Subquery(
            SaleReport.objects.filter(
                api_key=current_api_key,
            ).distinct('create_dt').values_list('id', flat=True))).order_by(
        '-date_from').values('week_num', 'year').annotate(
        date_to=Max(F('date_to')),
        date_from=Min(F('date_from')),
    ).values('year', 'week_num', 'date_from', 'date_to')

    return {'filter_period_queryset': filter_period_queryset}
