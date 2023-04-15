
from django.urls import path

from reports.views import DashboardView, ReportDetailView, EmptyReportsView

app_name = 'reports'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('reports/', EmptyReportsView.as_view(), name='empty_reports'),
    path('report/<str:create_dt>', ReportDetailView.as_view(), name='report_detail'),
]
