from django.urls import path

from payments.views import RedirectToRobokassaView, ReceiveResultView, SuccessPaymentView, FailPaymentView

app_name = 'payments'

urlpatterns = [
    # path('generate-robokassa-redirection/', RedirectToRobokassaView.as_view(), name='generate_robokassa_redirection'),
    # path('payment-result/', ReceiveResultView.as_view(), name='payment-result'),
    # path('success-payment/', SuccessPaymentView.as_view(), name='success_payment'),
    # path('fail-payment/', FailPaymentView.as_view(), name='fail_payment')
]
