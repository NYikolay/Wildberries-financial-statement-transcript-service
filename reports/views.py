import logging
from typing import List
from dateutil.relativedelta import relativedelta
import json

from django.shortcuts import render, redirect
from datetime import datetime, timedelta, date, timezone
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Subquery, Min, Max, F
from django.http import Http404
from django.contrib import messages
from django.core.cache import cache


from reports.forms import SaleReportForm
from reports.models import GeneralInformationObj, InfoTypes
from reports.services.generate_last_weeks_nums import get_last_weeks_nums
from reports.services.generate_reports import get_report
from reports.services.handle_graphs_filter_data import get_period_filter_data

from users.models import SaleReport, IncorrectReport, UnloadedReports

django_logger = logging.getLogger('django_logger')


class DashboardView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        if not current_api_key or not current_api_key.is_wb_data_loaded:
            return render(request, 'reports/empty_dashboard.html')

        try:
            period_filter_data: List[dict] = get_period_filter_data(dict(request.GET))
        except Exception as err:
            messages.error(request, 'Ошибка фильтрации периода.')
            return redirect('reports:dashboard')

        incorrect_reports_ids = IncorrectReport.objects.filter(
            api_key=current_api_key
        ).values_list('realizationreport_id', flat=True)

        filter_dates_queryset = SaleReport.objects.filter(
            id__in=Subquery(
                SaleReport.objects.filter(
                    api_key=current_api_key,
                ).distinct('create_dt').values_list('id', flat=True))).order_by(
            '-date_from').values('week_num', 'year').annotate(
            date_to=Max(F('date_to')),
            date_from=Min(F('date_from')),
        )

        try:
            report = get_report(request, current_api_key, period_filter_data)
        except Exception as err:
            django_logger.critical(
                f'It is impossible to calculate statistics in the dashboard for a user - {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Невозможно рассчитать статистику для отчётов. '
                                    'Пожалуйста, свяжитесь со службой поддержки.')
            return redirect('users:profile')

        report_by_products_json = json.dumps(report.get('report_by_products'))
        context = {
            'report': report,
            'report_by_products_json': report_by_products_json,
            'incorrect_reports_ids': incorrect_reports_ids,
            'filter_dates_data': filter_dates_queryset,
            'current_filter_data': period_filter_data,
            'is_unloaded_reports': UnloadedReports.objects.filter(api_key=current_api_key).exists()
        }
        return render(request, 'reports/dashboard.html', context)


class ReportDetailView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = SaleReportForm

    def get(self, request, create_dt):
        report_message = GeneralInformationObj.objects.filter(info_type=InfoTypes.reports, is_active=True).first()
        reports = SaleReport.objects.filter(
            api_key__is_current=True,
            api_key__user=request.user,
            create_dt__date=create_dt
        ).order_by('realizationreport_id')

        if len(reports) == 0:
            raise Http404

        blank_reports_list = SaleReport.objects.filter(
            Q(storage_cost__isnull=True) |
            Q(cost_paid_acceptance__isnull=True) |
            Q(other_deductions__isnull=True) |
            Q(supplier_costs__isnull=True),
            owner=request.user,
            api_key__is_current=True,
            api_key__user=request.user,
            ).values_list('create_dt', flat=True)

        create_dt_list = SaleReport.objects.filter(
            api_key__is_current=True, api_key__user=request.user).distinct('create_dt').order_by(
            '-create_dt').values('create_dt', 'week_num')

        context = {
            'create_dt_list': create_dt_list,
            'reports': reports,
            'blank_reports_list': blank_reports_list,
            'forms': [self.form_class(instance=report) for report in reports],
            'report_message': report_message
        }
        return render(request, 'reports/report_detail.html', context)

    def post(self, request, create_dt):

        storage_costs = request.POST.getlist('storage_cost')
        cost_paid_acceptances = request.POST.getlist('cost_paid_acceptance')
        other_deductions = request.POST.getlist('other_deductions')
        reports = SaleReport.objects.filter(
            api_key__is_current=True,
            api_key__user=request.user,
            create_dt__date=create_dt
        ).order_by('realizationreport_id')

        reports_forms = []

        for storage_cost, cost_paid, deduction, report in zip(
                storage_costs, cost_paid_acceptances, other_deductions, reports
        ):
            reports_forms.append(self.form_class({
                'storage_cost': storage_cost,
                'cost_paid_acceptance': cost_paid,
                'other_deductions': deduction,
                'supplier_costs': request.POST.get('supplier_costs')
            }, instance=report))

        if all([form.is_valid() for form in reports_forms]):
            for reports_form in reports_forms:
                reports_form.save()

            messages.success(request, 'Данные успешно сохранены.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        messages.error(
            request,
            'Произошла ошибка валидцаии формы. Убедитесь, что количество символов в полях не превышает 10.')

        context = {
            'create_dt_list': SaleReport.objects.filter(
                api_key__is_current=True, api_key__user=request.user).distinct('create_dt').order_by(
                '-create_dt').values('create_dt', 'week_num'),
            'reports': reports,
            'forms': reports_forms,
        }
        return render(request, 'reports/report_detail.html', context)


class EmptyReportsView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        if current_api_key and current_api_key.is_wb_data_loaded:
            return redirect('reports:report_detail', create_dt=SaleReport.objects.filter(
                api_key__is_current=True,
                api_key__user=request.user
            ).order_by('-create_dt').first().create_dt.strftime('%Y-%m-%d'))

        return render(request, 'reports/empty_reports.html')
