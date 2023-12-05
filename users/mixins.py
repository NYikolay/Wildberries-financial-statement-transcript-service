from django.shortcuts import redirect
from django.contrib import messages
from django_eventstream import send_event


class SubscriptionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_subscribed:
            messages.error(request, 'Для загрузки отчётов необходимо оплатить подписку.')
            return redirect('users:profile_subscriptions')

        return super().dispatch(request, *args, **kwargs)


class RedirectAuthenticatedUser:

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile_subscriptions')

        return super().dispatch(request, *args, **kwargs)
