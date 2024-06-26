import logging

from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from config.settings.base import ROBOKASSA_PASSWORD1, ROBOKASSA_MERCHANT_LOGIN
from payments.forms import RoboKassaForm, ResultURLForm, SuccessRedirectForm, FailRedirectForm
from payments.models import SuccessPaymentNotification, FailPaymentNotification
from payments.services.create_user_subscription_service import create_user_subscription
from payments.signals import result_received, fail_payment_signal
from support.tasks import send_user_report_to_chat
from users.models import Order, User
from payments.services.generating_redirect_link import generate_payment_link

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


django_logger = logging.getLogger('django_logger')


class RedirectToRobokassaView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = RoboKassaForm

    def get(self):
        return redirect('users:profile')

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            current_order = Order.objects.create(
                user=request.user
            )

            try:
                target_link = generate_payment_link(
                    ROBOKASSA_MERCHANT_LOGIN,
                    ROBOKASSA_PASSWORD1,
                    form.cleaned_data['OutSum'],
                    form.cleaned_data['Description'],
                    form.cleaned_data['IsTest'],
                    form.cleaned_data['CustomerEmail'],
                    form.cleaned_data['Culture'],
                    current_order.id,
                    form.cleaned_data['Receipt'],
                    user=form.cleaned_data['UserEmail'],
                    type=form.cleaned_data['SubscriptionType'],
                    discount=form.cleaned_data['Discount'],
                    duration=form.cleaned_data['Duration'],
                    durationdesc=form.cleaned_data['DurationDescription']
                )
            except Exception as err:
                django_logger.error(
                    f'Unable to generate a payment link for a user - {request.user.email}. Errors - {form.errors}',
                    exc_info=err)
                messages.error(
                    request,
                    'Невозможно сформировать ссылку на оплату. '
                    'Пожалуйста, повторите попытку или обратитесь в службу поддержки'
                )
                return redirect('users:profile')

            return redirect(target_link)

        django_logger.error(
            f'Unable to generate a payment link for a user - {request.user.email}. Errors - {form.errors}'
        )
        messages.error(
            request,
            'Невозможно сформировать ссылку на оплату. Пожалуйста, повторите попытку или обратитесь в службу поддержки'
        )
        return redirect('users:profile')


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveResultView(View):
    form_class = ResultURLForm

    def get(self):
        return redirect('users:profile')

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                current_user = User.objects.get(email=form.cleaned_data['Shp_user'])

                create_user_subscription(
                    current_user,
                    form.cleaned_data['Shp_type'],
                    form.cleaned_data['OutSum'],
                    form.cleaned_data['Shp_duration'],
                    form.cleaned_data['Shp_durationdesc'],
                    form.cleaned_data['Shp_discount']
                )
                send_user_report_to_chat.delay(F'Оплата подписки пользователем - {current_user.email} '
                                               F'на сумму {form.cleaned_data["OutSum"]} руб.')
            except Exception as err:
                django_logger.critical(
                    f'Subscription was not created for a user - {request.user.email}.',
                    exc_info=err
                )
                send_user_report_to_chat.delay(F'ОШИБКА!!!!! Оплата подписки пользователем - '
                                               F'{form.cleaned_data["Shp_user"]} '
                                               F'на сумму {form.cleaned_data["OutSum"]} руб.')

            inv_id, out_sum = form.cleaned_data['InvId'], form.cleaned_data['OutSum']
            notification = SuccessPaymentNotification.objects.create(inv_id=inv_id, out_sum=out_sum)
            result_received.send(sender=notification, InvId=inv_id, OutSum=out_sum)

            return HttpResponse('OK%s' % inv_id)
        django_logger.critical(
            f'Subscription was not created. Error: {form.errors}',
        )
        return HttpResponse('error: bad signature')


@method_decorator(csrf_exempt, name='dispatch')
class SuccessPaymentView(View):
    form_class = SuccessRedirectForm

    def get(self):
        return redirect('users:profile')

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            messages.success(request, 'Оплата прошла успешно')
            return redirect('users:profile')

        messages.success(
            request,
            'Оплата прошла успешно. В случае возникновения ошибок обратитесь в службу поддержки'
        )
        return redirect('users:profile')


@method_decorator(csrf_exempt, name='dispatch')
class FailPaymentView(View):
    form_class = FailRedirectForm

    def get(self):
        return redirect('users:profile')

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            inv_id, out_sum = form.cleaned_data['InvId'], form.cleaned_data['OutSum']
            notification = FailPaymentNotification.objects.create(inv_id=inv_id, out_sum=out_sum)
            fail_payment_signal.send(sender=notification, InvId=inv_id, OutSum=out_sum)

            messages.error(request, 'Оплата была отменена')
            return redirect('users:profile')

        messages.error(request, 'Оплата была отменена')
        return redirect('users:profile')


