import logging

from users.models import IncorrectReport


django_logger = logging.getLogger('django_logger')


def handle_incorrect_report_obj(request, report_data: dict, current_api_key):
    return IncorrectReport(
        api_key=current_api_key,
        owner=request.user,
        realizationreport_id=report_data.get('realizationreport_id'),
        date_from=report_data.get('date_from'),
        date_to=report_data.get('date_to')
    )


def generate_incorrect_reports(request, incorrect_reports_data_list: list, current_api_key) -> None:
    if len(incorrect_reports_data_list) == 0:
        IncorrectReport.objects.filter(owner=request.user, api_key=current_api_key).delete()
        return None

    generated_incorrect_reports = IncorrectReport.objects.filter(
        owner=request.user,
        api_key=current_api_key
    ).values_list('realizationreport_id', flat=True)

    incorrect_reports_objs_list = []

    for incorrect_report in incorrect_reports_data_list:
        if incorrect_report.get('realizationreport_id') not in generated_incorrect_reports:
            incorrect_reports_objs_list.append(handle_incorrect_report_obj(request, incorrect_report, current_api_key))

    try:
        if len(incorrect_reports_objs_list) > 0:
            IncorrectReport.objects.bulk_create(
                incorrect_reports_objs_list
            )

    except Exception as err:
        django_logger.error(f'Error during the loading of a broken report from a user - {request.user.email}')
