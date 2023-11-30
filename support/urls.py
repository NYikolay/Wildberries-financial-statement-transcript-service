from django.urls import path, re_path

from support.views import SupportRequestView, SupportInfoPage

app_name = 'support'

urlpatterns = [
    path('create-appeal/', SupportRequestView.as_view(), name='create_appeal'),
    path('', SupportInfoPage.as_view(), name='support')
]
