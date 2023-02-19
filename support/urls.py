from django.urls import path, re_path

from support.views import SupportRequestView

app_name = 'support'

urlpatterns = [
    path('create-appeal/', SupportRequestView.as_view(), name='create_appeal')
]
