from datetime import datetime
from dateutil.relativedelta import relativedelta


DECLINATION_DATE_DESC = {
    'week': ('неделя', 'недели', 'недель'),
    'month': ('месяц', 'месяца', 'месяцев'),
}


def get_subscribed_to_date(duration: int, duration_desc: str):
    current_date = datetime.now()

    if duration_desc.lower() in DECLINATION_DATE_DESC.get('week'):
        subscribed_to = current_date + relativedelta(weeks=duration)
    elif duration_desc.lower() in DECLINATION_DATE_DESC.get('month'):
        subscribed_to = current_date + relativedelta(months=duration)
    else:
        subscribed_to = datetime.now()

    return subscribed_to.replace(hour=0, minute=0, second=0, microsecond=0)
