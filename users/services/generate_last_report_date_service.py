from datetime import date
from dateutil.relativedelta import relativedelta

from users.models import IncorrectReport, SaleReport


def generate_date_by_months_filter(months_count: int):
    """
    Returns the date in string representation using the formula first day of month(today - 3 months)
    and get date of Monday this week
    :return: return string in format 'Y-m-d', ex.: '2023-12-01'
    """
    past_months_date = date.today() - relativedelta(months=months_count)
    first_date_of_month = past_months_date.replace(day=1)
    year = first_date_of_month.year - 1 if first_date_of_month.isocalendar()[1] == 52 else first_date_of_month.year
    last_report_date = date.fromisocalendar(
        year,
        first_date_of_month.isocalendar()[1],
        1
    ).strftime('%Y-%m-%d')

    return last_report_date


def get_last_report_date(current_api_key):
    if current_api_key.is_wb_data_loaded:
        if IncorrectReport.objects.filter(api_key=current_api_key).exists():
            last_report_date = IncorrectReport.objects.filter(
                api_key=current_api_key,
            ).earliest('date_from').date_from.strftime('%Y-%m-%d')
        else:
            last_report_date = SaleReport.objects.filter(
                api_key=current_api_key
            ).latest('create_dt').create_dt.strftime('%Y-%m-%d')
    else:
        last_report_date = generate_date_by_months_filter(3)

    return last_report_date

