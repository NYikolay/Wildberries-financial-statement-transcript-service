from django.contrib import admin
from django.urls import path, include

from django.views.decorators.cache import cache_page

from reports.views import DashboardView, ReportDetailView, EmptyReportsView

app_name = 'reports'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('reports/', EmptyReportsView.as_view(), name='empty_reports'),
    path('report/<str:create_dt>', ReportDetailView.as_view(), name='report_detail')
]
