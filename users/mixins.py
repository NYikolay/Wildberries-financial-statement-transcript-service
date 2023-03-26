from django.shortcuts import redirect
from django.contrib import messages


class SubscriptionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_subscribed:
            messages.error(request, 'Для загрузки отчёта необходимо оплатить подписку.')
            return redirect('users:profile')
        return super().dispatch(request, *args, **kwargs)
