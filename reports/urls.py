from django.urls import path
from django.views.decorators.cache import cache_page

from reports.views import (
    LoadReportAdditionalDataView,
    ReportsListView, DashboardMainView,
    DemoDashboardMainView, DashboardByBarcode, ExportReportByBarcodesView, DemoDashboardByBarcodeView,
    DashboardAbcXyzView, DemoDashboardAbcXyzView, ExportPenaltiesListView
)

app_name = 'reports'

urlpatterns = [
    path('', DashboardMainView.as_view(), name='dashboard_main'),
    path('demo/', cache_page(60*15)(DemoDashboardMainView.as_view()), name='demo_dashboard_main'),
    path(
        'demo/dashboard/barcode',
        cache_page(60*15)(DemoDashboardByBarcodeView.as_view()),
        name='demo_dashboard_by_barcode'
    ),
    path('dashboard/barcode/<int:barcode>/', DashboardByBarcode.as_view(), name='dashboard_by_barcode'),
    path('dashboard/abc-xyz/', DashboardAbcXyzView.as_view(), name='dashboard_abc_xyz'),
    path('export-penalties/', ExportPenaltiesListView.as_view(), name='export_penalties'),
    path(
        'demo/dashobard/abc-xyz/',
        cache_page(60*15)(DemoDashboardAbcXyzView.as_view()),
        name='demo_dashboard_abc_xyz'
    ),
    path('export-barcodes-detail', ExportReportByBarcodesView.as_view(), name='export_barcodes_detail'),
    path('reports/', ReportsListView.as_view(), name='reports_list'),
    path('set-report-add-data/', LoadReportAdditionalDataView.as_view(), name='set_report_add_data'),
]
