import json
import time
import logging
import pytz
from datetime import time as date_time, date, datetime
from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count, Exists, OuterRef, ExpressionWrapper, BooleanField, F
from django.views.generic.list import ListView
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse

from config.settings.base import REDIS_HOST, REDIS_PORT, SSE_NOTIFICATION_SECRET
from payments.models import SubscriptionTypes
from payments.services.create_user_subscription_service import create_user_subscription
from users.forms import (
    LoginForm, UserRegisterForm, APIKeyForm, ChangeUserPasswordForm, TaxRateForm,
    NetCostForm, PasswordResetEmailForm, UserPasswordResetForm, LoadNetCostsFileForm,
    ChangeCurrentApiKeyForm, CostsForm
)
from users.mixins import SubscriptionRequiredMixin, RedirectAuthenticatedUser
from users.models import User, WBApiKey, ClientUniqueProduct, TaxRate, NetCost, UserDiscount, SaleReport
from users.services.encrypt_api_key_service import get_encrypted_key
from users.services.email_services import send_email
from users.services.generate_subscriptions_data_service import get_user_subscriptions_data
from users.services.generate_excel_net_costs_example_service import generate_excel_net_costs_example
from users.services.generate_last_report_date_service import get_last_report_date
from users.services.handle_uploaded_netcosts_excel_service import handle_uploaded_net_costs
from users.services.wb_request_handling_services.execute_request_data_handling import \
    execute_wildberries_request_data_handling
from users.tasks import execute_wildberries_reports_loading
from users.token import account_activation_token, password_reset_token
from django.views.decorators.csrf import csrf_exempt

import redis
from celery.result import AsyncResult
from django_eventstream import send_event

django_logger = logging.getLogger('django_logger')


redis_instance = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=3)


class NotifySseUserView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        data = request.POST
        secret_key = data.get('secret')
        if secret_key and secret_key == SSE_NOTIFICATION_SECRET:
            user_id = data['user_id']
            status = data['status']
            message = data['message']

            send_event(
                f'user-{user_id}',
                'message',
                {"status": status, "message": message}
            )

            return JsonResponse({'status': "success"}, status=200)

        return JsonResponse({"error": "bas signature"}, status=400)


class RegisterPageView(RedirectAuthenticatedUser, CreateView):
    form_class = UserRegisterForm
    model = User
    success_url = reverse_lazy('users:email_confirmation_info')
    template_name = 'users/registration/register.html'
    activate_email_template_name = 'users/registration/account_activation.html'
    mail_subject = 'Подтверждение email на commery.ru'

    def form_valid(self, form):
        promo_code = form.cleaned_data.get('promo_code')
        user = form.save(commit=False)
        user.is_active = False
        user.promocode = promo_code
        user.save()

        if promo_code:
            current_date = datetime.now()
            discount_to = current_date + relativedelta(months=6)
            UserDiscount.objects.create(
                user=user,
                percent=promo_code.discount_percent,
                is_active=True,
                expiration_date=datetime.combine(discount_to, date_time.max)
            )

        current_site = get_current_site(self.request)
        send_email(
            user, current_site.domain, form.cleaned_data['email'], self.activate_email_template_name, self.mail_subject
        )

        self.request.session['new_email'] = form.cleaned_data['email']
        self.request.session['email_message_timestamp'] = time.time()

        return super().form_valid(form)


class ConfirmRegistrationView(RedirectAuthenticatedUser, View):
    login_url = 'users:login'

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            try:
                create_user_subscription(
                    current_user=user,
                    sub_type=SubscriptionTypes.TEST,
                    total_cost=0,
                    duration=1,
                    duration_description='неделя',
                    discount=0
                )
            except Exception as err:
                django_logger.critical(
                    f'Failed to issue a test subscription to a user - {user.email}.',
                    exc_info=err)

            messages.success(request, 'Благодарим за подтверждение почты. Вы можете войти в свой аккаунт')
            return redirect(self.login_url)

        messages.error(request, 'Ссылка повреждена или более недействительна')
        return redirect(self.login_url)


class ConfirmEmailPageView(RedirectAuthenticatedUser, View):
    template_name = 'users/registration/confirm_email.html'
    activate_email_template_name = 'users/registration/account_activation.html'
    mail_subject = 'Подтверждение email на commery.ru'

    def get(self, request):
        new_email = request.session.get('new_email', None)

        if new_email is None:
            messages.error(request, 'Отсутствует почта для подтверждения')
            return redirect('users:login')

        context = {'email': new_email}
        return render(request, self.template_name, context=context)

    def post(self, request):
        new_email = request.session.get('new_email', None)

        try:
            user = User.objects.get(email=request.session.get('new_email'), is_active=False)
        except ObjectDoesNotExist:

            messages.error(request, 'Отсутствует почта для подтверждения.')
            return render(request, self.template_name, context={'email': new_email})

        email_timestamp_subtracting = time.time() - request.session.get('email_message_timestamp', 0)

        if email_timestamp_subtracting < 60:
            messages.error(request, 'Отправить письмо повторно можно раз в 60 секунд.')
            return render(request, self.template_name, context={'email': new_email})

        current_site = get_current_site(self.request)
        send_email(user, current_site.domain, user.email, self.activate_email_template_name, self.mail_subject)

        self.request.session['email_message_timestamp'] = time.time()

        messages.success(request, 'Письмо для активации аккаунта было повторно отправлено на указанный email.')
        return render(request, self.template_name, context={'email': new_email})


class LoginPageView(RedirectAuthenticatedUser, View):
    template_name = 'users/authentication/login.html'
    form_class = LoginForm
    activate_email_template_name = 'users/registration/account_activation.html'
    mail_subject = 'Подтверждение email на commery.ru'

    def get(self, request):
        context = {
            'form': self.form_class()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.cleaned_data['user']

            if not user.is_active:
                current_site = get_current_site(self.request)
                send_email(
                    user, current_site.domain, form.cleaned_data['email'], self.activate_email_template_name,
                    self.mail_subject
                )

                self.request.session['new_email'] = form.cleaned_data['email']
                self.request.session['email_message_timestamp'] = time.time()

                return redirect('users:email_confirmation_info')

            login(request, user)
            return redirect('users:profile_subscriptions')

        context = {'form': form}
        return render(request, self.template_name, context=context)


class LogoutView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def post(self, request):
        logout(request)
        messages.success(request, "Выход был выполнен успешно")
        return redirect(self.login_url)


class ProfileSubscriptionsPage(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    template_name = "users/profile/subscriptions.html"

    def get(self, request):
        subscriptions = get_user_subscriptions_data(request.user)

        context = {
            'current_subscription': subscriptions.get('current_subscription'),
            'subscriptions': subscriptions.get('subscriptions_data'),
            'is_active_subscription_exists': request.user.is_subscribed
        }

        return render(request, self.template_name, context=context)


class CreateApiKeyView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    template_name = 'users/profile/companies/create_api_key.html'
    redirect_url = "users:companies_list"
    form_class = APIKeyForm

    def get(self, request):
        context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request):
        api_keys_count = request.user.keys.count()
        form = self.form_class(request.POST, api_keys_count=api_keys_count)

        if form.is_valid():

            api_key_obj = form.save(commit=False)
            api_key_obj.api_key = get_encrypted_key(form.cleaned_data['api_key'])
            api_key_obj.user = request.user

            if api_keys_count > 0:
                api_key_obj.is_current = False

            api_key_obj.save()

            return redirect(self.redirect_url)

        context = {"form": form}
        return render(request, self.template_name, context)


class ChangeCurrentApiKeyView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = ChangeCurrentApiKeyForm

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            current_api_key = request.user.keys.filter(is_current=True).first()
            api_key = request.user.keys.filter(id=form.cleaned_data['api_key_id']).first()

            if not api_key:
                django_logger.error(f"Changing api key with incorrect id for user - {request.user.email}")
                messages.error(request, "Невозможно сменить подключение. Передан некорректный Api ключ")
                return redirect("users:companies_list")

            with transaction.atomic():
                current_api_key.is_current = False
                api_key.is_current = True
                current_api_key.save()
                api_key.save()

            messages.success(request, "Подключение было успешно изменено.")
            return redirect("users:companies_list")

        django_logger.error(f"Error while change Api Key. User - {request.user.email}")

        messages.error(request, "Невозможно сменить подключение.")
        return redirect("users:companies_list")


class CompaniesListView(ListView):
    template_name = 'users/profile/companies/companies_list.html'
    unauthorized_template_name = 'users/profile/companies/unauthorized_companies.html'
    context_object_name = 'companies'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, self.unauthorized_template_name)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.keys.order_by('-is_current', '-last_reports_update')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_keys_count'] = self.request.user.keys.count()

        return context


class UpdateApiKeyView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    template_name = 'users/profile/companies/edit_api_key.html'
    redirect_url = "users:companies_list"
    form_class = APIKeyForm

    def get(self, request, api_key_id):
        api_key = get_object_or_404(WBApiKey, pk=api_key_id, user=request.user)
        form = self.form_class(instance=api_key)

        return render(request, self.template_name, context={"form": form, "api_key": api_key})

    def post(self, request, api_key_id):
        company = get_object_or_404(WBApiKey, pk=api_key_id, user=request.user)
        form = self.form_class(data=request.POST, instance=company)

        if form.is_valid():
            api_key_obj = form.save(commit=False)

            if api_key_obj.api_key != company.api_key:
                api_key_obj.api_key = get_encrypted_key(form.cleaned_data['api_key'])

            api_key_obj.save()

            return redirect(self.redirect_url)

        return render(request, self.template_name, context={"form": form, "api_key": company})


class DeleteApiKeyView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    success_redirect_url = "users:companies_list"

    def post(self, request, api_key_id):
        for_delete_api_key = get_object_or_404(WBApiKey, pk=api_key_id, user=request.user)
        for_current_api_key = request.user.keys.filter(
            ~Q(pk=for_delete_api_key.id)
        ).order_by(
            '-is_current', '-last_reports_update'
        ).first()

        with transaction.atomic():
            for_delete_api_key.delete()

            if for_current_api_key:
                for_current_api_key.is_current = True
                for_current_api_key.save()

        messages.success(request, 'Подключение было успешно остановлено')
        return redirect(self.success_redirect_url)


class ChangePasswordView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    template_name = 'users/profile/password/password_change.html'
    form_class = ChangeUserPasswordForm

    def get(self, request):
        context = {"form": self.form_class(user=request.user)}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST, user=request.user)

        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)

            messages.success(request, "Пароль был успешно обновлён")
            return render(request, self.template_name, context={"form": self.form_class()})

        return render(request, self.template_name, context={"form": form})


class PasswordResetView(RedirectAuthenticatedUser, View):
    form_class = PasswordResetEmailForm
    template_name = 'users/profile/password/password_reset_form.html'
    reset_email_template_name = 'users/profile/password/password_reset_email.html'
    redirect_url = 'users:password_reset_done'
    mail_subject = 'Подтверждение сброса пароля'

    def get(self, request):
        return render(request, self.template_name, context={'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.cleaned_data['user']
            current_site = get_current_site(self.request)
            send_email(
                user,
                current_site.domain,
                form.cleaned_data['email'],
                self.reset_email_template_name,
                self.mail_subject,
                is_reset_password=True
            )
            return redirect(self.redirect_url)

        return render(request, self.template_name, context={'form': form})


class PasswordResetConfirmView(RedirectAuthenticatedUser, View):
    form_class = UserPasswordResetForm
    redirect_url = 'users:login'
    template_name = 'users/profile/password/password_reset_confirm.html'

    def get(self, request, token, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError):
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            context = {
                'form': self.form_class(user),
                'uid': uidb64,
                'token': token
            }
            return render(request, self.template_name, context=context)

        messages.error(request, 'Ссылка повреждена или более недействительна.')
        return redirect(self.redirect_url)

    def post(self, request, token, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError):
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            form = self.form_class(user=user, data=request.POST)

            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)

                messages.success(request, 'Пароль был успешно изменён.')
                return redirect('users:login')

            context = {'form': form, 'uid': uidb64, 'token': token}
            return render(request, self.template_name, context=context)

        messages.error(request, 'Ссылка повреждена или более недействительна.')
        return redirect(self.redirect_url)


class PasswordResetDoneView(RedirectAuthenticatedUser, View):
    template_name = 'users/profile/password/password_reset_done.html'

    def get(self, request):
        return render(request, self.template_name)


class TaxRateListView(ListView):
    template_name = 'users/profile/taxes/taxes.html'
    unauthorized_template_name = 'users/profile/taxes/unauthorized_taxes.html'
    form_class = TaxRateForm
    context_object_name = 'tax_rates'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, self.unauthorized_template_name)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = TaxRate.objects.filter(
            api_key__is_current=True, api_key__user=self.request.user
        ).order_by('commencement_date')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        context['tax_rates_forms'] = [self.form_class(instance=tax_rate) for tax_rate in self.object_list]
        return context


class CreateTaxRateView(LoginRequiredMixin, CreateView):
    login_url = 'users:login'
    redirect_field_name = 'login'
    success_url = reverse_lazy("users:profile_taxes")
    form_class = TaxRateForm
    model = TaxRate

    def get_queryset(self):
        queryset = TaxRate.objects.filter(
            api_key__is_current=True, api_key__user=self.request.user
        )
        return queryset

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Не удалось создать налог, пожалуйста, убедитесь что все поля заполнены корректно'
        )

        return redirect(self.request.META.get('HTTP_REFERER', '/'))

    def form_valid(self, form):
        api_key = self.request.user.keys.filter(is_current=True).first()

        if not api_key:
            messages.error(self.request, "Отсутствует подключение к Wildberries")
            return redirect(self.success_url)

        tax_rates_count = api_key.taxes.count()

        if tax_rates_count >= 3:
            messages.error(self.request, "Нельзя создать более 3-х ставок налога.")
            return redirect(self.success_url)

        tax_rate = form.save(commit=False)

        tax_rate.api_key = api_key
        tax_rate.save()

        return super().form_valid(form)


class DeleteTaxRateView(LoginRequiredMixin, DeleteView):
    model = TaxRate
    login_url = 'users:login'
    redirect_field_name = 'login'
    success_url = reverse_lazy("users:profile_taxes")
    pk_url_kwarg = 'id'

    def get_queryset(self):
        queryset = TaxRate.objects.filter(
            api_key__is_current=True, api_key__user=self.request.user
        )
        return queryset

    def get_success_url(self):
        messages.success(self.request, 'Ставка налога успешно удалена')
        return reverse_lazy("users:profile_taxes")


class ChangeTaxRateView(LoginRequiredMixin, UpdateView):
    form_class = TaxRateForm
    success_url = reverse_lazy("users:profile_taxes")
    pk_url_kwarg = 'id'

    def get_queryset(self):
        queryset = TaxRate.objects.filter(
            api_key__is_current=True, api_key__user=self.request.user
        )
        return queryset

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Не удалось обновить налог, пожалуйста, убедитесь что все поля заполнены корректно'
        )

        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class CostsListView(ListView):
    template_name = 'users/profile/costs/costs.html'
    unauthorized_template_name = 'users/profile/costs/unauthorized_costs.html'
    context_object_name = 'costs'
    form_class = CostsForm
    model = SaleReport

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, self.unauthorized_template_name)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        reports = (self.model.objects.filter(owner=self.request.user, api_key__is_current=True)
                   .only('id', 'week_num', 'date_from', 'date_to', 'create_dt', 'supplier_costs')
                   .distinct('create_dt')
                   .order_by('-create_dt'))

        return [{"object": report, "costs_form": self.form_class(instance=report)} for report in reports]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context


class ChangeCostsView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    success_url = reverse_lazy("users:costs_list")
    form_class = CostsForm
    model = SaleReport

    def post(self, request, create_dt):
        form = self.form_class(request.POST)

        if form.is_valid():
            if self.request.GET.get("forDelete") == "true":
                costs = None
            else:
                costs = form.cleaned_data['supplier_costs']

            self.model.objects.filter(
                api_key__is_current=True,
                api_key__user=request.user,
                create_dt__date=create_dt
            ).update(supplier_costs=costs)

            return redirect(self.success_url)

        messages.error(self.request, "Значение расходов не может содержать более 11 символов до запятой")
        return redirect(self.success_url)


class EmptyProductsView(View):
    template_name = 'users/profile/products/unauthorized_products.html'

    def get(self, request):
        return render(request, self.template_name)


class ProductDetailView(LoginRequiredMixin, DetailView):
    login_url = 'users:login'
    redirect_field_name = 'login'
    template_name = 'users/profile/products/products.html'
    pk_url_kwarg = 'article'
    context_object_name = 'product'
    model = ClientUniqueProduct
    paginator_class = Paginator
    form_class = LoadNetCostsFileForm
    net_cost_form = NetCostForm

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            self.model,
            api_key__user=self.request.user,
            api_key__is_current=True,
            nm_id=self.kwargs.get('article')
        )

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')

        products = self.model.objects.filter(
            api_key__user=self.request.user, api_key__is_current=True
        ).annotate(
            has_net_cost=ExpressionWrapper(Q(cost_prices__isnull=False), output_field=BooleanField())
        ).values('image', 'nm_id', 'product_name', 'has_net_cost').distinct().order_by('brand', 'nm_id')

        paginator = self.paginator_class(products, 4)

        paginator_products = paginator.get_page(page)

        context['products'] = paginator_products
        context['file_form'] = self.form_class()
        context['net_costs'] = [
            {
                "object": net_cost,
                "form": self.net_cost_form(instance=net_cost)
            }
            for net_cost in self.object.cost_prices.all().order_by('cost_date')
        ]
        context['net_cost_form'] = self.net_cost_form(initial={"product": self.object})

        return context


class CreateNetCostView(LoginRequiredMixin, CreateView):
    login_url = 'users:login'
    redirect_field_name = 'login'
    model = NetCost
    form_class = NetCostForm

    def get_queryset(self):
        queryset = self.model.objects.filter(
            product__api_key__user=self.request.user,
            product__api_key__is_current=True
        )

        return queryset

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Не удалось создать себестоимость, пожалуйста, убедитесь что все поля заполнены корректно'
        )

        return redirect(self.request.META.get('HTTP_REFERER', '/'))

    def get_success_url(self):
        messages.success(self.request, 'Себестоимость успешно создана')
        return reverse_lazy("users:product_detail", args=(self.object.product.nm_id,))


class UpdateNetCostView(LoginRequiredMixin, UpdateView):
    login_url = 'users:login'
    redirect_field_name = 'login'
    model = NetCost
    pk_url_kwarg = 'id'
    form_class = NetCostForm

    def get_queryset(self):
        queryset = self.model.objects.filter(
            product__api_key__user=self.request.user,
            product__api_key__is_current=True
        )

        return queryset

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Не удалось обновить себестоимость, пожалуйста, убедитесь что все поля заполнены корректно'
        )
        return redirect(self.request.META.get('HTTP_REFERER', '/'))

    def get_success_url(self):
        messages.success(self.request, 'Себестоимость успешно изменена')
        return reverse_lazy("users:product_detail", args=(self.object.product.nm_id,))


class DeleteNetCostView(LoginRequiredMixin, DeleteView):
    login_url = 'users:login'
    redirect_field_name = 'login'
    pk_url_kwarg = 'id'
    model = NetCost

    def get_queryset(self):
        queryset = self.model.objects.filter(
            product__api_key__user=self.request.user,
            product__api_key__is_current=True
        )

        return queryset

    def get_success_url(self):
        messages.success(self.request, 'Себестоимость успешно удалена')
        return reverse_lazy("users:product_detail", args=(self.object.product.nm_id,))


class ExecuteLoadingReportsFromWildberriesView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def post(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        if not current_api_key:
            messages.error(request, 'Для загрузки отчёта о продажах, пожалуйста, создайте API ключ Wildberries')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if current_api_key.is_active_import:
            messages.error(request, 'Происходит загрузка отчётов. Пожалуйста, дождитесь завершения')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        execute_wildberries_reports_loading.delay(current_api_key.id, request.user.id)

        messages.success(request, 'Отчёты будут загружены в скором времени. Пожалуйста, дождитесь завершения')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class LoadDataFromWBView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def post(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()
        today_date = date.today()

        if not current_api_key:
            messages.error(request, 'Для загрузки отчёта о продажах, пожалуйста, создайте API ключ Wildberries')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if current_api_key.is_active_import:
            messages.error(request, 'Происходит загрузка отчётов. Пожалуйста, дождитесь завершения')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        current_api_key.is_active_import = True
        current_api_key.save()
        last_report_date = get_last_report_date(current_api_key)

        try:
            report_status = execute_wildberries_request_data_handling(
                request.user,
                last_report_date,
                today_date,
                current_api_key
            )
        except Exception as err:
            django_logger.critical(
                f'Failed to load reports for a user {request.user.email}',
                exc_info=err
            )

            current_api_key.is_active_import = False
            current_api_key.save()

            messages.error(request, 'Ошибка формирования отчёта. Пожалуйста, обратитесь в службу поддержки.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if report_status.get('status') is True:
            current_api_key.is_wb_data_loaded = True
            current_api_key.is_active_import = False
            current_api_key.last_reports_update = datetime.now().replace(tzinfo=pytz.timezone('Europe/Moscow'))
            current_api_key.save()

            messages.success(request, 'Данные успешно загружены')
            return redirect('reports:dashboard')

        current_api_key.is_active_import = False
        current_api_key.save()

        messages.error(request, f'{report_status.get("message")}')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class ExportNetCostsExampleView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    model = ClientUniqueProduct

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        products = self.model.objects.filter(
            api_key=current_api_key
        ).annotate(
            net_cots_amount=F('cost_prices__amount'),
            net_costs_date=F('cost_prices__cost_date')
        ).values_list('nm_id', 'net_cots_amount', 'net_costs_date').order_by('nm_id', 'net_costs_date')

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="net_costs_temp.xlsx"'

        work_book = generate_excel_net_costs_example(products)
        work_book.save(response)
        return response


class SetNetCostsFromFileView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = LoadNetCostsFileForm

    def post(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            try:
                handled_file_result = handle_uploaded_net_costs(request.FILES['net_costs_file'], current_api_key)
            except Exception as err:
                django_logger.error(
                    f'Unsuccessful attempt to load costs through a file by a user {request.user.email}',
                    exc_info=err
                )
                messages.error(
                    request,
                    'Ошиба обработки файла. Пожалуйста, обратитесь в службу поддержки'
                )
                return redirect(request.META.get('HTTP_REFERER', '/'))

            if handled_file_result.get('status') is False:
                messages.error(request, handled_file_result.get('message'))
                return redirect(request.META.get('HTTP_REFERER', '/'))

            messages.success(request, handled_file_result.get('message'))
            return redirect(request.META.get('HTTP_REFERER', '/'))

        messages.error(
            request,
            'Не удалось загрузить файл. Пожалуйста, убедитесь, что расширение загружаемого файла - .xlsx'
        )
        return redirect(request.META.get('HTTP_REFERER', '/'))



