from django.shortcuts import render
from django.views.generic import View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from config.settings.base import EMAIL_HOST_USER
from support.forms import SupportRequestForm
from support.tasks import send_user_report_to_chat
from users.tasks import send_email_verification


class SupportRequestView(LoginRequiredMixin, View):
    login_url = 'users:login'
    redirect_field_name = 'login'
    form_class = SupportRequestForm

    def post(self, request):
        form = self.form_class(request.POST)

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
            })
        return JsonResponse({
            'status': False,
            'message': f'Произошла ошибка отправки сообщения. Пожалуйста, убедитесь что все поля заполнены верно.'
        })