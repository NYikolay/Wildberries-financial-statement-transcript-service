import datetime
import json
import logging
from typing import List

from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.http import HttpResponse, Http404
from django.contrib import messages

from reports.forms import LoadReportAdditionalDataFrom
from reports.mixins import RedirectUnauthenticatedToDemo
from reports.services.execute_generating_reports_services import get_full_user_report, get_report_by_barcode, \
    get_report_by_barcodes
from reports.services.generating_export_dataframe import get_barcodes_detail_dataframe

from reports.services.get_filters_db_data_service import get_filters_db_data
from reports.services.handle_graphs_filter_data import get_filter_data
from reports.services.handle_report_additional_data_filte_service import create_reports_additional_data
from reports.services.report_generation_services.get_demo_dashboard_data_services import get_demo_dashboard_data, \
    get_demo_dashboard_by_barcode_data, get_demo_xyz_abc_data

from users.models import SaleReport, IncorrectReport, UnloadedReports, WBApiKey, SaleObject

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


class DemoDashboardMainView(View):
    template_name = 'reports/demo_dashboard_main.html'

    def get(self, request):
        report = get_demo_dashboard_data()
        return render(request, self.template_name, {"report": report})


class DemoDashboardByBarcodeView(View):
    template_name = 'reports/demo_dashboard_by_barcode.html'

    def get(self, request):
        report = get_demo_dashboard_by_barcode_data()
        return render(request, self.template_name, {"report": report})


class DemoDashboardAbcXyzView(View):
    template_name = 'reports/demo_abc_xyz.html'

    def get(self, request):
        report = get_demo_xyz_abc_data()
        return render(request, self.template_name, {"report": report})


class DashboardMainView(RedirectUnauthenticatedToDemo, View):
    template_name = 'reports/dashboard_main.html'
    reverse_redirect_demo_url = 'reports:demo_dashboard_main'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        if not current_api_key or not current_api_key.is_wb_data_loaded:
            return redirect(self.reverse_redirect_demo_url)

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


class DashboardByBarcode(RedirectUnauthenticatedToDemo, View):
    template_name = 'reports/dashboard_by_barcodes.html'
    reverse_redirect_demo_url = 'reports:demo_dashboard_by_barcode'

    def get(self, request, barcode):
        current_api_key = request.user.keys.filter(is_current=True).first()
        is_barcode_exists = SaleObject.objects.filter(api_key=current_api_key, barcode=barcode).exists()

        if not is_barcode_exists:
            raise Http404('Данного баркода не существует')

        if not current_api_key or not current_api_key.is_wb_data_loaded:
            return redirect(self.reverse_redirect_demo_url)

        try:
            current_filter_data: List[dict] = get_filter_data(dict(request.GET))
        except Exception as err:
            django_logger.critical(
                f'Unable to filter data by period in the report for the user- {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Ошибка фильтрации периода')
            return redirect('reports:dashboard_main')

        try:
            report_by_barcodes = get_report_by_barcode(
                request.user,
                current_api_key,
                current_filter_data,
                barcode
            )
        except Exception as err:
            django_logger.critical(
                f'It is impossible to calculate statistics in the barcodes detail for a user - {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Невозможно рассчитать статистику для баркода. '
                                    'Пожалуйста, свяжитесь со службой поддержки')
            return redirect('reports:dashboard_main')

        filters_data: dict = get_filters_db_data(current_api_key)

        context = {
            'report': report_by_barcodes,
            'filters_data': filters_data,
            'current_filter_data': current_filter_data,
            'current_barcode': str(barcode)
        }

        return render(request, self.template_name, context)


class DashboardAbcXyzView(RedirectUnauthenticatedToDemo, View):
    template_name = 'reports/dashboard_abc_xyz.html'
    reverse_redirect_demo_url = 'reports:demo_dashboard_abc_xyz'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        if not current_api_key or not current_api_key.is_wb_data_loaded:
            return redirect(self.reverse_redirect_demo_url)

        try:
            current_filter_data: List[dict] = get_filter_data(dict(request.GET))
        except Exception as err:
            django_logger.critical(
                f'Unable to filter data by period in the report for the user- {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Ошибка фильтрации периода')
            return redirect('reports:dashboard_main')

        try:
            report_by_barcodes = get_report_by_barcodes(
                request.user,
                current_api_key,
                current_filter_data,
                True
            )
        except Exception as err:
            django_logger.critical(
                f'It is impossible to calculate statistics in the barcodes detail for a user - {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Невозможно рассчитать статистику для баркода. '
                                    'Пожалуйста, свяжитесь со службой поддержки')
            return redirect('reports:dashboard_main')

        filters_data: dict = get_filters_db_data(current_api_key)

        context = {
            'report': report_by_barcodes,
            'filters_data': filters_data,
            'current_filter_data': current_filter_data,
        }

        return render(request, self.template_name, context)


class ExportReportByBarcodesView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        try:
            current_filter_data: List[dict] = get_filter_data(dict(request.GET))
        except Exception as err:
            django_logger.critical(
                f'Unable to filter data by period in the report for the user- {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Ошибка фильтрации периода')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            report_by_barcodes = get_report_by_barcodes(request.user, current_api_key, current_filter_data)
        except Exception as err:
            django_logger.critical(
                f'It is impossible to calculate statistics in the barcodes detail for a user - {request.user.email}',
                exc_info=err
            )
            messages.error(request, 'Невозможно рассчитать статистику для товаров. '
                                    'Пожалуйста, свяжитесь со службой поддержки')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = \
            f'attachment; filename="barcodes_detail_report_{datetime.datetime.now().strftime("%d.%m.%Y")}.xlsx"'

        report_by_barcodes_df = get_barcodes_detail_dataframe(report_by_barcodes.get('products_calculated_values'))
        report_by_barcodes_df.to_excel(response, index=False)

        return response


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
