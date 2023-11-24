from django.urls import path

from reports.views import (
    LoadReportAdditionalDataView,
    ReportsListView, DashboardMainView,
    DemoDashboardMainView, DashboardByBarcode, ExportReportByBarcodesView, DemoDashboardByBarcodeView
)

app_name = 'reports'

urlpatterns = [
    path('', DashboardMainView.as_view(), name='dashboard_main'),
    path('demo/', DemoDashboardMainView.as_view(), name='demo_dashboard_main'),
    path('demo/dashboard/barcode', DemoDashboardByBarcodeView.as_view(), name='demo_dashboard_by_barcode'),
    path('dashboard/barcode/<int:barcode>/', DashboardByBarcode.as_view(), name='dashboard_by_barcode'),
    path('export-barcodes-detail', ExportReportByBarcodesView.as_view(), name='export_barcodes_detail'),
    path('reports/', ReportsListView.as_view(), name='reports_list'),
    path('set-report-add-data/', LoadReportAdditionalDataView.as_view(), name='set_report_add_data'),
]
