from datetime import date
from dateutil.relativedelta import relativedelta


def get_last_report_date():
    three_months_ago_date = date.today() - relativedelta(months=3)
    first_date_of_month = three_months_ago_date.replace(day=1)
    year = first_date_of_month.year - 1 if first_date_of_month.isocalendar()[1] == 52 else first_date_of_month.year
    last_report_date = date.fromisocalendar(
        year,
        first_date_of_month.isocalendar()[1], 1).strftime('%Y-%m-%d')
    return last_report_date
