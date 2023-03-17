from datetime import datetime, timezone

from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from config.settings.base import ROBOKASSA_PASSWORD1, ROBOKASSA_MERCHANT_LOGIN
from payments.forms import RoboKassaForm, ResultURLForm, SuccessRedirectForm, FailRedirectForm
from payments.models import SuccessPaymentNotification, FailPaymentNotification, SubscriptionType
from payments.services.generating_subscribed_to_date import get_subscribed_to_date
from payments.signals import result_received, fail_payment_signal
from users.models import Order, User, UserSubscription
from payments.services.generating_redirect_link import generate_payment_link

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class RedirectToRobokassaView(LoginRequiredMixin, View):
    form_class = RoboKassaForm

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():

            current_order = Order.objects.create(
                user=request.user
            )

            target_link = generate_payment_link(
                ROBOKASSA_MERCHANT_LOGIN,
                ROBOKASSA_PASSWORD1,
                form.cleaned_data['OutSum'],
                form.cleaned_data['Description'],
                form.cleaned_data['IsTest'],
                form.cleaned_data['CustomerEmail'],
                form.cleaned_data['Culture'],
                current_order.id,
                user=form.cleaned_data['UserEmail'],
                type=form.cleaned_data['SubscriptionType'],
                discount=form.cleaned_data['Discount'],
                duration=form.cleaned_data['Duration'],
                durationdesc=form.cleaned_data['DurationDescription']
            )

            return redirect(target_link)

        return redirect('users:profile')


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveResultView(View):
    form_class = ResultURLForm

    def post(self, request):
        form = ResultURLForm(request.POST)

        if form.is_valid():
            inv_id, out_sum = form.cleaned_data['InvId'], form.cleaned_data['OutSum']

            notification = SuccessPaymentNotification.objects.create(inv_id=inv_id, out_sum=out_sum)

            result_received.send(sender=notification, InvId=inv_id, OutSum=out_sum)

            return HttpResponse('OK%s' % inv_id)

        return HttpResponse('error: bad signature')


@method_decorator(csrf_exempt, name='dispatch')
class SuccessPaymentView(View):
    form_class = SuccessRedirectForm

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['Shp_user'])
            user.is_subscribed = True
            user.save()
            print(form.cleaned_data)
            subscription_type_obj = SubscriptionType.objects.get(type=form.cleaned_data['Shp_type'])

            UserSubscription.objects.create(
                subscription_type=subscription_type_obj,
                user=user,
                subscribed_from=datetime.now(),
                total_cost=form.cleaned_data['OutSum'],
                subscribed_to=get_subscribed_to_date(
                    form.cleaned_data['Shp_duration'],
                    form.cleaned_data['Shp_durationdesc']
                ),
                discount_percent=form.cleaned_data['Shp_discount'],
                is_active=True,

            )

            messages.success(request, 'Оплата прошла успешно')
            return redirect('users:profile')

        messages.error(
            request,
            'Оплата не удалась. Если средства были списаны, пожалуйста, свяжитесь со службой поддержки'
        )

        return redirect('users:profile')


@method_decorator(csrf_exempt, name='dispatch')
class FailPaymentView(View):
    form_class = FailRedirectForm

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            inv_id, out_sum = form.cleaned_data['InvId'], form.cleaned_data['OutSum']

            notification = FailPaymentNotification.objects.create(inv_id=inv_id, out_sum=out_sum)

            fail_payment_signal.send(sender=notification, InvId=inv_id, OutSum=out_sum)

            messages.error(
                request,
                'Оплата неудалась или была отменена. '
                'Если средства были списаны, пожалуйста, свяжитесь со службой поддержки.'
            )

            return redirect('users:profile')

        messages.error(
            request,
            'Оплата неудалась или была отменена. '
            'Если средства были списаны, пожалуйста, свяжитесь со службой поддержки.'
        )

        return redirect('users:profile')


