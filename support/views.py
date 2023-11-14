from django.shortcuts import render
from django.views.generic import View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import F
from config.settings.base import EMAIL_HOST_USER
from support.forms import SupportRequestForm
from support.tasks import send_user_report_to_chat
from users.models import ClientUniqueProduct
from users.tasks import send_email_verification


class SupportInfoPage(View):
    template_name = "support/support.html"

    def get(self, request):
        return render(request, self.template_name)


class SupportRequestView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = SupportRequestForm

    def post(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = self.form_class(request.POST)

        if is_ajax:
            if form.is_valid():
                form.save()

                mail_subject = f'Обращение от пользователя {request.user.email} ' \
                               f'на тему: {form.cleaned_data["message_type"]}'
                message = f'Данные заявки: {request.user.email} ' \
                          f'\nДополнительные данные: ' \
                          f'\nИмя - {form.cleaned_data["user_name"]} ' \
                          f'\nТема обращения - {form.cleaned_data["message_type"]} ' \
                          f'\nСообщение - {form.cleaned_data["message"]}'

                send_user_report_to_chat.delay(message)
                send_email_verification.delay(message, EMAIL_HOST_USER, mail_subject)

                return JsonResponse({
                    'status': True,
                    'message': 'Благодарим за обращение. Ответ будет выслан на почту, указанную при регистрации.'
                }, status=200)

            return JsonResponse({
                'status': False,
                'message': f'Произошла ошибка отправки сообщения. Пожалуйста, убедитесь что все поля заполнены верно.'
            }, status=400)
        return HttpResponseBadRequest('Invalid request')
