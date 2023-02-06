from django.test import TestCase
from django.test.client import RequestFactory, Client

from reports.services.generate_reports import generate_report_by_products
from reports.views import DashboardView

