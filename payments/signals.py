from django.dispatch import Signal


result_received = Signal()
success_payment_signal = Signal()
fail_payment_signal = Signal()
