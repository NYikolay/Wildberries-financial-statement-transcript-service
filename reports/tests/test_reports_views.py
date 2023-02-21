import json

from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.urls import reverse

from reports.views import DashboardView
from users.models import SaleObject, SaleReport, WBApiKey, User
