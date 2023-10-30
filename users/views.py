import time
from datetime import datetime, time as date_time
import logging
import pytz
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from urllib.parse import urlencode

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views.generic import View, CreateView
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
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

from users.tasks import send_email_verification
from users.token import account_activation_token, password_reset_token


django_logger = logging.getLogger('django_logger')


class RegisterPageView(CreateView):
    form_class = UserRegisterForm
    model = User
    success_url = reverse_lazy('users:email_confirmation_info')
    template_name = 'users/registration/register.html'
    activate_email_template_name = 'users/profile/password/password_reset_email.html'
    mail_subject = 'Подтверждение email на commery.ru'

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        promo_code = form.cleaned_data['promo_code']
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

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
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
            return redirect('users:login')

        messages.error(request, 'Ссылка повреждена или более недействительна')
        return redirect('users:login')


class ConfirmEmailPageView(View):

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        new_email = request.session.get('new_email', None)

        if new_email is None:
            messages.error(request, 'Отсутствует почта для подтверждения')
            return redirect('users:login')

        context = {'email': new_email}
        return render(request, 'users/registration/confirm_email.html', context=context)

    def post(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            try:
                user = User.objects.get(email=request.session.get('new_email'), is_active=False)
            except Exception as err:
                return JsonResponse(
                    {
                        'status': False,
                        'message': 'Отсутствует почта для подтверждения'
                    }, status=400
                )

            email_timestamp_subtracting = time.time() - request.session.get('email_message_timestamp', 0)

            if email_timestamp_subtracting < 60:
                return JsonResponse(
                    {
                        'status': False,
                        'message': 'Перед повторным подтверждением необходимо подождать 60 секунд.'
                    }, status=429
                )

            current_site = get_current_site(self.request)
            mail_message = render_to_string('users/registration/account_activation.html', {
                'user': user,
                'protocol': 'https',
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            send_email_verification.delay(mail_message, user.email, 'Подтверждение email на COMMERY.RU')

            self.request.session['email_message_timestamp'] = time.time()
            return JsonResponse(
                {
                    'status': True,
                    'message': 'На ваш почтовый ящик было повторно отправлено письмо для подтверждения.'
                }, status=200
            )
        return HttpResponseBadRequest('Invalid request')


class LoginPageView(View):
    template_name = 'users/authentication/login.html'
    form_class = LoginForm
    activate_email_template_name = 'users/profile/password/password_reset_email.html'
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
            return redirect('reports:dashboard')

        context = {'form': form}
        return render(request, self.template_name, context=context)


class LogoutView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):
        logout(request)
        return redirect('users:login')


class ProfilePage(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def get(self, request):

        subscriptions = get_user_subscriptions_data(request.user)

        context = {
            'api_keys': request.user.keys.filter(),
            'profile_form': ChangeUserDataForm(instance=request.user),
            'change_password_form': ChangeUserPasswordForm(),
            'subscriptions': subscriptions,
            'is_active_subscription_exists': request.user.is_subscribed
        }
        return render(request, 'users/profile/profile.html', context)


class ChangeProfileData(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = ChangeUserDataForm

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно обновлены')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class ChangePasswordView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = ChangeUserPasswordForm

    def post(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = self.form_class(request.POST)
        if is_ajax:
            if form.is_valid():
                if not request.user.check_password(form.cleaned_data['old_password']):
                    return JsonResponse(
                        {
                            'status': False,
                            'message': f'Старый пароль введён неверно.'
                        }
                    )
                user = request.user
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)
                return JsonResponse(
                    {
                        'status': True,
                        'message': f'Пароль успешно обновлён.'
                    },
                    status=200
                )
            return JsonResponse(
                {
                    'status': False,
                    'message': f'{form.non_field_errors().as_text()}'
                },
                status=400
            )
        return HttpResponseBadRequest('Invalid request')


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
                self.mail_subject
            )
            return redirect('users:password_reset_done')

        return render(request, self.template_name, context={'form': form})


class PasswordResetConfirmView(View):
    form_class = UserPasswordResetForm

    def get(self, request, token, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError):
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            context = {
                'form': UserPasswordResetForm(user),
                'uid': uidb64,
                'token': token
            }
            return render(request, 'users/profile/password/password_reset_confirm.html', context=context)

        messages.error(request, 'Ссылка повреждена или более недействительна.')
        return redirect('users:login')

    def post(self, request, token, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except(TypeError, ValueError, OverflowError):
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            form = UserPasswordResetForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)

                messages.success(request, 'Пароль был успешно изменён.')
                return redirect('users:login')
            context = {
                'form': form,
                'uid': uidb64,
                'token': token
            }
            return render(request, 'users/profile/password/password_reset_confirm.html', context=context)

        messages.error(request, 'Ссылка повреждена или более недействительна.')
        return redirect('users:login')


class PasswordResetDoneView(View):

    @redirect_authenticated_user
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'users/profile/password/password_reset_done.html')


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


class CompaniesListView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    api_key_form = APIKeyForm
    tax_rate_form = TaxRateForm

    def get(self, request):
        context = {
            'api_keys': request.user.keys.all(),
            'api_key_form': self.api_key_form(),
            'tax_rate_form': self.tax_rate_form()
        }
        return render(request, 'users/profile/companies/companies_list.html', context)

    def post(self, request):
        tax_rates = list(filter(None, request.POST.getlist('tax_rate')))
        commencement_dates = list(filter(None, request.POST.getlist('commencement_date')))

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

        api_key_form = self.api_key_form(request.POST)

        if api_key_form.is_valid() and all([form.is_valid() for form in tax_rates_forms]):
            if WBApiKey.objects.filter(user=request.user).exists():
                messages.error(request, 'Для вашего аккаунта нельзя создавать более 1 API ключа')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            try:
                with transaction.atomic():
                    api_key_obj = api_key_form.save(commit=False)
                    api_key_obj.api_key = get_encrypted_key(api_key_form.cleaned_data['api_key'])
                    api_key_obj.user = request.user
                    api_key_obj.save()

                    for tax_rate_form in tax_rates_forms:
                        tax_rate_obj = tax_rate_form.save(commit=False)
                        tax_rate_obj.api_key = api_key_obj
                        tax_rate_obj.save()
            except Exception as err:
                django_logger.error(f'Error when creating a store for a user {request.user.email}. '
                                    f'Failed to save values in the database in a transaction', exc_info=err)
                messages.error(
                    request,
                    'Не удалось создать магазин. Пожалуйста, повторите попытку или свяжитесь со службой поддержки.'
                )
                return redirect(request.META.get('HTTP_REFERER', '/'))

            messages.success(request, 'Магазин успешно создан')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        return render(request, 'users/profile/companies/companies_list.html', context={'api_key_form': api_key_form})


class DeleteCompanyView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'

    def post(self, request, api_key_id):
        company = get_object_or_404(WBApiKey, pk=api_key_id, user=request.user)
        company.delete()

        messages.success(request, 'Магазин успешно удалён!')
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



