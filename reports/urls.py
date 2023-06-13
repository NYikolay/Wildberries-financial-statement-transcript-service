
from django.urls import path

from reports.views import DashboardView, ReportDetailView, EmptyReportsView, LoadReportAdditionalDataView, \
    ReportByBarcodeView, ReportByBarcodesView, ExportReportByBarcodesView

app_name = 'reports'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('barcodes-detail/', ReportByBarcodesView.as_view(), name='barcodes_detail'),
    path('export-barcodes-detail', ExportReportByBarcodesView.as_view(), name='export_barcodes_detail'),
    path('reports/', EmptyReportsView.as_view(), name='empty_reports'),
    path('report/<str:create_dt>', ReportDetailView.as_view(), name='report_detail'),
    path('set-report-add-data/', LoadReportAdditionalDataView.as_view(), name='set_report_add_data'),
    path('get-barcode-detail/', ReportByBarcodeView.as_view(), name='get_barcode_detail')
]
