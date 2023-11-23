import datetime
import json
import logging
from typing import List, Union

import pandas as pd
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.db.models import Q, QuerySet, Count, Case, When, IntegerField, BooleanField
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib import messages

from reports.forms import SaleReportForm, LoadReportAdditionalDataFrom, ReportByBarcodeForm
from reports.mixins import RedirectUnauthenticatedToDemo
from reports.services.execute_generating_reports_services import get_full_user_report, get_detail_report_by_barcode, \
    get_report_by_barcodes
from reports.services.generating_export_dataframe import get_barcodes_detail_dataframe

from reports.services.get_filters_db_data_service import get_filters_db_data
from reports.services.handle_graphs_filter_data import get_filter_data
from reports.services.handle_report_additional_data_filte_service import create_reports_additional_data
from reports.services.report_generation_services.get_demo_dashboard_data_services import get_demo_dashboard_data

from users.models import SaleReport, IncorrectReport, UnloadedReports, WBApiKey

django_logger = logging.getLogger('django_logger')


class ReportsListView(ListView):
    model = SaleReport
    template_name = 'reports/reports_list.html'
    unauthorized_template_name = 'reports/unauthorized_reports_list.html'
    context_object_name = 'reports'
    form_class = LoadReportAdditionalDataFrom

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, self.unauthorized_template_name)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        incorrect_reports = IncorrectReport.objects.filter(owner=self.request.user, api_key__is_current=True)

        correct_reports = (self.model.objects
                           .filter(owner=self.request.user, api_key__is_current=True)
                           .order_by('-create_dt')
                           )

        queryset = {"correct_reports": correct_reports, "incorrect_reports": incorrect_reports}

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context


class DemoDashboardMinView(View):
    template_name = 'reports/empty_dashboard.html'

    def get(self, request):
        report = get_demo_dashboard_data()
        return render(request, self.template_name, {"report": report})


class DashboardMainView(RedirectUnauthenticatedToDemo, View):
    template_name = 'reports/dashboard_main.html'
    redirect_demo_url = 'reports:demo_dashboard_main'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        if not current_api_key or not current_api_key.is_wb_data_loaded:
            return redirect(self.redirect_demo_url)

        try:
            current_filter_data: List[dict] = get_filter_data(dict(request.GET))
        except Exception as err:
            django_logger.critical(
                f'Unable to filter data by period in the report for the user- {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Ошибка фильтрации периода')
            return redirect('reports:dashboard_main')

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
            return redirect('reports:reports_list')

        return render(
            request, self.template_name, {
                "report": report,
                'filters_data': filters_data,
                'current_filter_data': current_filter_data
            }
        )


class ReportByBarcodesView(LoginRequiredMixin, View):
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

        try:
            report_by_barcodes = get_report_by_barcodes(
                request.user,
                current_api_key,
                current_filter_data
            )
        except Exception as err:
            django_logger.critical(
                f'It is impossible to calculate statistics in the barcodes detail for a user - {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Невозможно рассчитать статистику для товаров. '
                                    'Пожалуйста, свяжитесь со службой поддержки')
            return redirect('reports:dashboard')

        filters_data: dict = get_filters_db_data(current_api_key)

        context = {
            'report_by_barcodes': json.dumps(report_by_barcodes),
            'filters_data': filters_data,
            'current_filter_data': current_filter_data,
        }

        return render(request, 'reports/dashboard_by_barcodes.html', context)


class ExportReportByBarcodesView(LoginRequiredMixin, View):
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

        report_by_barcodes = get_report_by_barcodes(request.user, current_api_key, current_filter_data)

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = \
            f'attachment; filename="barcodes_detail_report_{datetime.datetime.now().strftime("%d.%m.%Y")}.xlsx"'

        report_by_barcodes_df = get_barcodes_detail_dataframe(report_by_barcodes)
        report_by_barcodes_df.to_excel(response, index=False)

        return response


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
                    report_by_barcode = get_detail_report_by_barcode(
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
                return redirect("reports:reports_list")
            if file_handling_status:
                messages.success(
                    request,
                    'Значения успешно обновлены'
                )
                return redirect("reports:reports_list")
            else:
                messages.error(
                    request,
                    'Ошибка валидации файла. Пожалуйста, убедитесь в корректности данных внутри файла'
                )
                return redirect("reports:reports_list")

        messages.error(
            request,
            'Не удалось загрузить файл. Пожалуйста, убедитесь, что расширение загружаемого файла - .xlsx'
        )
        return redirect("reports:reports_list")


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


class DemoDashboardView(View):

    def get(self, request):

        return render(request, '')
