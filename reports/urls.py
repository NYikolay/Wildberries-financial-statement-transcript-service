
from django.urls import path

from reports.views import DashboardView, ReportDetailView, EmptyReportsView, LoadReportAdditionalDataView, \
    ReportByBarcodeView, ReportByBarcodesView, ExportReportByBarcodesView, ReportsListView, DashboardMainView

app_name = 'reports'

urlpatterns = [
    path('', DashboardMainView.as_view(), name='dashboard_main'),
    path('reports/', ReportsListView.as_view(), name='reports_list'),
    path('barcodes-detail/', ReportByBarcodesView.as_view(), name='barcodes_detail'),
    path('export-barcodes-detail', ExportReportByBarcodesView.as_view(), name='export_barcodes_detail'),
    path('report/<str:create_dt>', ReportDetailView.as_view(), name='report_detail'),
    path('set-report-add-data/', LoadReportAdditionalDataView.as_view(), name='set_report_add_data'),
    path('get-barcode-detail/', ReportByBarcodeView.as_view(), name='get_barcode_detail')
]
