import time
from datetime import time as date_time
import logging
import pytz
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from urllib.parse import urlencode

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list import ListView
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views.generic import View, CreateView
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest

from payments.models import SubscriptionTypes
from payments.services.create_user_subscription_service import create_user_subscription
from users.decorators import redirect_authenticated_user
from users.forms import (LoginForm, UserRegisterForm, APIKeyForm,
                         ChangeUserDataForm, ChangeUserPasswordForm, TaxRateForm,
                         UpdateAPIKeyForm, NetCostForm, PasswordResetEmailForm, UserPasswordResetForm,
                         LoadNetCostsFileForm)
from users.mixins import SubscriptionRequiredMixin
from users.models import User, WBApiKey, ClientUniqueProduct, TaxRate, NetCost, UserDiscount
from users.services.encrypt_api_key_service import get_encrypted_key
from users.services.email_services import send_email
from users.services.generate_subscriptions_data_service import get_user_subscriptions_data
from users.services.generate_excel_net_costs_example_service import generate_excel_net_costs_example
from users.services.generate_last_report_date_service import get_last_report_date
from users.services.handle_uploaded_netcosts_excel_service import handle_uploaded_net_costs
from users.services.wb_request_handling_services.execute_request_data_handling import \
    execute_wildberries_request_data_handling

from users.token import account_activation_token, password_reset_token


django_logger = logging.getLogger('django_logger')


class RegisterPageView(CreateView):
    form_class = UserRegisterForm
    model = User
    success_url = reverse_lazy('users:email_confirmation_info')
    template_name = 'users/registration/register.html'
    activate_email_template_name = 'users/registration/account_activation.html'
    mail_subject = 'Подтверждение email на commery.ru'

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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


class ConfirmRegistrationView(View):
    login_url = 'users:login'

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
                django_logger.info(
                    f'Failed to issue a test subscription to a user - {user.email}.',
                    exc_info=err)

            messages.success(request, 'Благодарим за подтверждение почты. Вы можете войти в свой аккаунт')
            return redirect(self.login_url)

        messages.error(request, 'Ссылка повреждена или более недействительна')
        return redirect(self.login_url)


class ConfirmEmailPageView(View):
    template_name = 'users/registration/confirm_email.html'
    activate_email_template_name = 'users/registration/account_activation.html'
    mail_subject = 'Подтверждение email на commery.ru'

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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


class LoginPageView(View):
    template_name = 'users/authentication/login.html'
    form_class = LoginForm
    activate_email_template_name = 'users/registration/account_activation.html'
    mail_subject = 'Подтверждение email на commery.ru'

    @redirect_authenticated_user
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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

    def get(self, request):
        logout(request)
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

            return redirect("users:companies_list")

        context = {"form": form}
        return render(request, self.template_name, context)


class CompaniesListView(LoginRequiredMixin, ListView):
    login_url = 'users:login'
    redirect_field_name = 'login'
    template_name = 'users/profile/companies/companies_list.html'
    model = WBApiKey
    context_object_name = 'companies'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_keys_count'] = self.request.user.keys.count()
        return context


class UpdateApiKeyView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    template_name = 'users/profile/companies/edit_api_key.html'
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

            return redirect("users:companies_list")


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


class PasswordResetView(View):
    form_class = PasswordResetEmailForm
    template_name = 'users/profile/password/password_reset_form.html'
    reset_email_template_name = 'users/profile/password/password_reset_email.html'
    mail_subject = 'Подтверждение сброса пароля'

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
            return redirect('users:password_reset_done')

        return render(request, self.template_name, context={'form': form})


class PasswordResetConfirmView(View):
    form_class = UserPasswordResetForm
    template_name = 'users/profile/password/password_reset_confirm.html'

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
        return redirect('users:login')

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
        return redirect('users:login')


class PasswordResetDoneView(View):
    template_name = 'users/profile/password/password_reset_done.html'

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name)


class CompanyEditView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    api_key_form = UpdateAPIKeyForm
    tax_rate_form = TaxRateForm

    def get(self, request, api_key_id):
        company = get_object_or_404(WBApiKey, pk=api_key_id, user=request.user)
        context = {
            'company': company,
            'api_key_form': self.api_key_form(instance=company),
            'taxes': company.taxes.all()
        }
        return render(request, 'users/profile/companies/company_edit.html', context=context)

    def post(self, request, api_key_id):
        tax_rates = list(filter(None, request.POST.getlist('tax_rate')))
        commencement_dates = list(filter(None, request.POST.getlist('commencement_date')))

        company = get_object_or_404(WBApiKey, pk=api_key_id, user=request.user)
        api_key_form = self.api_key_form(request.POST, instance=company)

        if all([
            (len(tax_rates) != len(commencement_dates)) and (len(tax_rates) <= 3 or len(commencement_dates) <= 3)
        ]):
            django_logger.info(f'Removed js validation, an attempt to bypass security. User - {request.user.email}.')
            messages.error(
                request,
                'Ошибка валидации значений налогов. Количестно ставок налога не может быть больше 3. '
                'Количестно ставок налога должно соответствовать количеству дат начала действия'
            )
            return redirect(request.META.get('HTTP_REFERER', '/'))

        tax_rates_forms = []

        for tax, date in zip(tax_rates, commencement_dates):
            tax_rates_forms.append(self.tax_rate_form({'tax_rate': tax, 'commencement_date': date}))

        decrypted_api_key = company.api_key

        if api_key_form.is_valid() and all([form.is_valid() for form in tax_rates_forms]):
            try:
                with transaction.atomic():
                    api_key_obj = api_key_form.save(commit=False)
                    if api_key_obj.api_key != decrypted_api_key:
                        api_key_obj.api_key = get_encrypted_key(api_key_form.cleaned_data['api_key'])
                    api_key_obj.save()

                    TaxRate.objects.filter(api_key=company).delete()

                    for tax_rate_form in tax_rates_forms:
                        tax_rate_obj = tax_rate_form.save(commit=False)
                        tax_rate_obj.api_key = company
                        tax_rate_obj.save()
            except Exception as err:
                django_logger.error(f'Error when updating the store for a user {request.user.email}. '
                                    f'Failed to save values in the database in a transaction', exc_info=err)
                messages.error(
                    request,
                    'Не удалось обновить магазин. Пожалуйста, повторите попытку или свяжитесь со службой поддержки.'
                )
                return redirect(request.META.get('HTTP_REFERER', '/'))

            messages.success(request, 'Магазин успешно обновлён')
            return redirect('users:companies_list')

        context = {
            'api_key_form': api_key_form,
            'company': company,
            'taxes': company.taxes.all()
        }

        return render(request, 'users/profile/companies/company_edit.html', context=context)


class DeleteCompanyView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    success_redirect_url = "users:companies_list"

    def post(self, request, api_key_id):
        company = get_object_or_404(WBApiKey, pk=api_key_id, user=request.user)
        company.delete()

        messages.success(request, 'Подключение было успешно остановлено')
        return redirect(self.success_redirect_url)


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


class CheckReportsLoadingStatus(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):
        api_key_reports_loading_status = request.user.keys.filter(is_current=True).values('is_active_import').first()
        return JsonResponse(
            {
                "status": api_key_reports_loading_status
            }
        )


class EmptyProductsListView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()

        if current_api_key and current_api_key.is_products_loaded:
            return redirect('users:product_detail', ClientUniqueProduct.objects.filter(
                api_key__is_current=True, api_key__user=request.user
            ).order_by('brand', 'nm_id').values_list('nm_id', flat=True)[:1].first())

        return render(request, 'users/profile/products/empty_products.html')


class ProductDetailView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request, article_value):
        product = get_object_or_404(ClientUniqueProduct,
                                    api_key__user=request.user,
                                    api_key__is_current=True,
                                    nm_id=article_value
                                    )

        products_objs_list = ClientUniqueProduct.objects.filter(
            api_key__user=request.user, api_key__is_current=True
        ).order_by('brand', 'nm_id')

        product_paginator = Paginator(products_objs_list, 8)
        page_number = request.GET.get('page')
        page_obj = product_paginator.get_page(page_number)
        net_costs = product.cost_prices.all().order_by('cost_date')

        context = {
            'products': page_obj,
            'product': product,
            'net_costs': net_costs,
            'net_costs_load_form': LoadNetCostsFileForm()
        }
        return render(request, 'users/profile/products/product_detail.html', context)


class EditProductView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = NetCostForm

    def get(self, request, article_value):
        product = get_object_or_404(
            ClientUniqueProduct,
            nm_id=article_value,
            api_key__user=request.user,
            api_key__is_current=True
        )

        products_objs_list = ClientUniqueProduct.objects.filter(
            api_key__user=request.user, api_key__is_current=True
        ).order_by('brand', 'nm_id')

        product_paginator = Paginator(products_objs_list, 8)
        page_number = request.GET.get('page')
        page_obj = product_paginator.get_page(page_number)

        net_costs = product.cost_prices.all().order_by('cost_date')
        context = {
            'products': page_obj,
            'product': product,
            'net_costs': net_costs,
            'form': self.form_class(),
            'net_costs_load_form': LoadNetCostsFileForm()
        }
        return render(request, 'users/profile/products/edit_product.html', context)

    def post(self, request, article_value):
        cost_inputs = list(filter(None, request.POST.getlist('cost_input')))
        product_cost_dates = list(filter(None, request.POST.getlist('product_cost_date')))

        if len(cost_inputs) != len(product_cost_dates):
            messages.error(
                request,
                'Ошибка валидации значений себестоимости.'
                'Количестно ставок налога должно соответствовать количеству дат начала действия.'
            )
            return redirect(request.META.get('HTTP_REFERER', '/'))

        product = get_object_or_404(
            ClientUniqueProduct,
            nm_id=article_value,
            api_key__user=request.user,
            api_key__is_current=True
        )
        net_costs_forms = []

        for cost, date in zip(cost_inputs, product_cost_dates):
            net_costs_forms.append(self.form_class({'amount': cost, 'cost_date': date}))

        if all([form.is_valid() for form in net_costs_forms]):

            NetCost.objects.filter(product=product).delete()

            for form in net_costs_forms:
                net_cost_obj = form.save(commit=False)
                net_cost_obj.product = product
                net_cost_obj.save()

            messages.success(request, 'Данные успешно сохранены!')

            base_url = reverse('users:product_detail', kwargs={'article_value': product.nm_id})
            query_string = urlencode({'page': request.GET.get('page')})
            url = f'{base_url}?{query_string}'

            return redirect(url)

        messages.error(
            request,
            'Произошла ошибка валидцаии формы. Убедитесь, что количество символов в полях не превышает 13')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class ExportNetCostsExampleView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):
        current_api_key = request.user.keys.filter(is_current=True).first()
        net_costs_set = NetCost.objects.filter(
            product__api_key=current_api_key
        ).values_list('product__nm_id', 'amount', 'cost_date')

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="net_costs_temp.xlsx"'

        work_book = generate_excel_net_costs_example(net_costs_set)
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
                    'Ошиба обработки файла. Пожалуйста, обратитесь в службу поддержки.'
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



