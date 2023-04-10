
from django.db.models import Q


def generate_period_filter_conditions(period_filter_data: list):
    """
    The function forms an instance of the Q() class to filter
    :param period_filter_data: It can be empty.
    A list containing a dictionary with year (List[int]) and week_nums (List[int]) as keys.
    :return: An instance of class Q with data for filtering
    """

    period_q_obj = Q()
    category_q_obj = Q()
    brand_q_obj = Q()

    for filter_data in period_filter_data:
        if filter_data.get('year') or filter_data.get('week_nums'):
            period_q_obj |= Q(year=filter_data.get('year'), week_num__in=filter_data.get('week_nums'))
        if filter_data.get('subject_name'):
            category_q_obj |= Q(subject_name__in=filter_data.get('subject_name'))
        if filter_data.get('brand_name'):
            brand_q_obj |= Q(brand_name__in=filter_data.get('brand_name'))

    return {
        'period_q_obj': period_q_obj,
        'category_q_obj': category_q_obj,
        'brand_q_obj': brand_q_obj
    }
