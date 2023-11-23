
from django.urls import path

from reports.views import EmptyReportsView, LoadReportAdditionalDataView, \
    ReportByBarcodeView, ReportByBarcodesView, ExportReportByBarcodesView, ReportsListView, DashboardMainView, \
    DemoDashboardMinView

app_name = 'reports'

urlpatterns = [
    path('', DashboardMainView.as_view(), name='dashboard_main'),
    path('demo/', DemoDashboardMinView.as_view(), name='demo_dashboard_main'),
    path('reports/', ReportsListView.as_view(), name='reports_list'),
    path('barcodes-detail/', ReportByBarcodesView.as_view(), name='barcodes_detail'),
    path('export-barcodes-detail', ExportReportByBarcodesView.as_view(), name='export_barcodes_detail'),
    path('set-report-add-data/', LoadReportAdditionalDataView.as_view(), name='set_report_add_data'),
    path('get-barcode-detail/', ReportByBarcodeView.as_view(), name='get_barcode_detail')
]
