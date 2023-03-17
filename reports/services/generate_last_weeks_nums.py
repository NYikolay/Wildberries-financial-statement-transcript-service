from datetime import datetime, date
from typing import List
from dateutil.relativedelta import relativedelta
from calendar import monthrange

from django.core.cache import cache
from django.shortcuts import redirect


def get_last_weeks_nums(request) -> List[int]:
    if request.GET.get('month') and request.GET.get('year'):

        if not request.GET.get('month').isdigit() or not request.GET.get('year').isdigit():
            return redirect('reports:dashboard')

        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
        if cache.get(f'{request.user.id}_report'):
            cache.delete(f'{request.user.id}_report')
        all_weeks = [date(year, month, day).isocalendar()[1] for day in
                     range(1, monthrange(year, month)[1])]
        last_weeks_nums: List[int] = list(set(all_weeks))
        return last_weeks_nums

    last_weeks_nums: List[int] = [(datetime.today() - relativedelta(weeks=i)).isocalendar().week for i in
                                  range(24)]
    return last_weeks_nums
