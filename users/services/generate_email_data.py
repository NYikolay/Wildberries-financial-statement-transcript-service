from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from users.token import account_activation_token


def get_email_data(user, domain):

    mail_message = render_to_string('users/registration/account_activation.html', {
        'user': user,
        'protocol': 'https',
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })

    mail_subject = 'Подтверждение email на COMMERY.RU'

    return {
        'mail_message': mail_message,
        'mail_subject': mail_subject
    }
