from django.contrib import admin

from payments.models import SubscriptionType, SuccessPaymentNotification, FailPaymentNotification

admin.site.register(SubscriptionType)
admin.site.register(SuccessPaymentNotification)
admin.site.register(FailPaymentNotification)
