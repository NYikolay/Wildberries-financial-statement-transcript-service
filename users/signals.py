from django.dispatch import receiver

from users.models import Order
from payments.signals import result_received, fail_payment_signal


@receiver(result_received)
def payment_received(sender, **kwargs):
    order = Order.objects.get(pk=kwargs['InvId'])
    order.status = 'paid'
    order.paid_sum = kwargs['OutSum']
    order.save()


@receiver(fail_payment_signal)
def payment_failed(sender, **kwargs):
    order = Order.objects.get(pk=kwargs['InvId'])
    order.status = 'fail'
    order.paid_sum = kwargs['OutSum']
    order.save()
