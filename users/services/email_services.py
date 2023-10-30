from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from users.token import account_activation_token
from users.tasks import send_email_verification


def get_email_data(user, domain, template_message_name, mail_subject):

    mail_message = render_to_string(template_message_name, {
        'user': user,
        'protocol': 'https',
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })

    return {
        'mail_message': mail_message,
        'mail_subject': mail_subject
    }


def send_email(user, domain, email, template_message_name, mail_subject):
    email_data = get_email_data(user, domain, template_message_name, mail_subject)
    send_email_verification.delay(
        email_data.get('mail_message'),
        email,
        email_data.get('mail_subject')
    )
