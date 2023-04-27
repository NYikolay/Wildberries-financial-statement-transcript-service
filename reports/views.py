import logging
from typing import List, Union

from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.contrib import messages

from reports.forms import SaleReportForm, LoadReportAdditionalDataFrom, ReportByBarcodeForm
from reports.services.execute_generating_report_service import get_full_user_report, get_report_by_barcode

from reports.services.get_filters_db_data_service import get_filters_db_data
from reports.services.handle_graphs_filter_data import get_filter_data
from reports.services.handle_report_additional_data_filte_service import create_reports_additional_data

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
            current_filter_data: List[dict] = get_filter_data(dict(request.GET))
        except Exception as err:
            django_logger.critical(
                f'Unable to filter data by period in the report for the user- {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Ошибка фильтрации периода')
            return redirect('reports:dashboard')

        incorrect_reports_ids: Union[QuerySet, List[int]] = IncorrectReport.objects.filter(
            api_key=current_api_key
        ).values_list('realizationreport_id', flat=True)

        filters_data: dict = get_filters_db_data(current_api_key)

        try:
            report = get_full_user_report(request.user, current_api_key, current_filter_data)
        except Exception as err:
            django_logger.critical(
                f'It is impossible to calculate statistics in the dashboard for a user - {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Невозможно рассчитать статистику для отчётов. '
                                    'Пожалуйста, свяжитесь со службой поддержки')
            return redirect('users:profile')

        context = {
            'report': report,
            'incorrect_reports_ids': incorrect_reports_ids,
            'filters_data': filters_data,
            'current_filter_data': current_filter_data,
            'is_unloaded_reports': UnloadedReports.objects.filter(api_key=current_api_key).exists()
        }
        return render(request, 'reports/dashboard.html', context)


class ReportByBarcodeView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = ReportByBarcodeForm

    def post(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = self.form_class(request.POST)

        if is_ajax:
            if form.is_valid():
                current_api_key = request.user.keys.filter(is_current=True).first()
                try:
                    report_by_barcode = get_report_by_barcode(
                        request.user, current_api_key, form.cleaned_data['period_filters'],
                        form.cleaned_data['barcode'], form.cleaned_data['nm_id'])
                except Exception as err:
                    django_logger.critical(
                        f'It is impossible to calculate statistics in the dashboard by barcode for a user - '
                        f'{request.user.email}',
                        exc_info=err
                    )
                    return JsonResponse({'status': False}, status=400)
                data = {
                    'status': True,
                    **report_by_barcode,
                    'barcode': form.cleaned_data['barcode'],
                    'abc_group': form.cleaned_data['abc_group'],
                    'xyz_group': form.cleaned_data['xyz_group'],
                    'nm_id': form.cleaned_data['nm_id'],
                    'image': form.cleaned_data['image'],
                    'product_name': form.cleaned_data['product_name']
                }
                return JsonResponse(data, status=200)
            return JsonResponse({'status': False}, status=400)
        return HttpResponseBadRequest('Invalid request')


class ReportDetailView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = SaleReportForm

    def get(self, request, create_dt):
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
            'file_load_form': LoadReportAdditionalDataFrom()
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
            'Произошла ошибка валидцаии формы. Убедитесь, что количество символов в полях не превышает 13')

        context = {
            'create_dt_list': SaleReport.objects.filter(
                api_key__is_current=True, api_key__user=request.user).distinct('create_dt').order_by(
                '-create_dt').values('create_dt', 'week_num'),
            'reports': reports,
            'forms': reports_forms,
        }
        return render(request, 'reports/report_detail.html', context)


class LoadReportAdditionalDataView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = LoadReportAdditionalDataFrom

    def post(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            try:
                file_handling_status = create_reports_additional_data(
                    request.FILES['report_data_file'], current_api_key
                )
            except Exception as err:
                django_logger.info(
                    f'Error setting report values via file for a user - {request.user.email}',
                    exc_info=err
                )
                messages.error(
                    request,
                    'Не удалось обработать файл. Пожалуйста, убедитесь в корректности данных внутри файла'
                )
                return redirect(request.META.get('HTTP_REFERER', '/'))
            if file_handling_status:
                messages.success(
                    request,
                    'Значения успешно обновлены'
                )
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                messages.error(
                    request,
                    'Ошибка валидации файла. Пожалуйста, убедитесь в корректности данных внутри файла'
                )
                return redirect(request.META.get('HTTP_REFERER', '/'))
        messages.error(
            request,
            'Не удалось загрузить файл. Пожалуйста, убедитесь, что расширение загружаемого файла - .xlsx'
        )
        return redirect(request.META.get('HTTP_REFERER', '/'))


class EmptyReportsView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        if current_api_key and current_api_key.is_wb_data_loaded:
            return redirect(
                'reports:report_detail', create_dt=SaleReport.objects.filter(
                    api_key=current_api_key).order_by('-create_dt').first().create_dt.strftime('%Y-%m-%d'))

        return render(request, 'reports/empty_reports.html')
