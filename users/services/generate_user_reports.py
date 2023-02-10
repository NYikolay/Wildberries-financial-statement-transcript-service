import uuid

from users.models import SaleObject, SaleReport


def create_report_object(request, api_key, sale, unique_week_uuid):
    return SaleReport(
        api_key=api_key,
        owner=request.user,
        realizationreport_id=sale.realizationreport_id,
        unique_week_uuid=unique_week_uuid,
        year=sale.year,
        week_num=sale.week_num,
        month_num=sale.month_num,
        create_dt=sale.create_dt,
        date_from=sale.date_from,
        date_to=sale.date_to
    )


def generate_reports(request, api_key):
    sale_objects = SaleObject.objects.filter(
        owner=request.user,
        api_key=api_key
    ).distinct('realizationreport_id').order_by('realizationreport_id')

    report_objects = []

    unique_weeks_uuid = {}

    for sale in sale_objects:
        if SaleReport.objects.filter(api_key__is_current=True,
                                     api_key__user=request.user,
                                     realizationreport_id=sale.realizationreport_id).exists():
            continue

        if unique_weeks_uuid.get(sale.week_num, None):
            report_objects.append(create_report_object(request, api_key, sale, unique_weeks_uuid.get(sale.week_num)))
        else:
            new_uuid = uuid.uuid4()
            unique_weeks_uuid[sale.week_num] = new_uuid
            report_objects.append(create_report_object(request, api_key, sale, new_uuid))

    SaleReport.objects.bulk_create(report_objects)

