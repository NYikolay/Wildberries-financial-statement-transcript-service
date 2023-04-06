
from django.db.models import Q


def generate_period_filter_conditions(period_filter_data: list):
    """
    The function forms an instance of the Q() class to filter
    :param period_filter_data: It can be empty.
    A list containing a dictionary with year (List[int]) and week_nums (List[int]) as keys.
    :return: An instance of class Q with data for filtering
    """
    empty_q_obj = Q()

    for filter_data in period_filter_data:
        empty_q_obj |= Q(year=filter_data.get('year'), week_num__in=filter_data.get('week_nums'))

    return empty_q_obj
