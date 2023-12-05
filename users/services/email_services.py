from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from users.token import account_activation_token, password_reset_token
from users.tasks import send_email_verification


def send_email(user, domain, email, template_message_name, mail_subject, is_reset_password = False):
    mail_message = render_to_string(template_message_name, {
        'user': user,
        'protocol': 'https',
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user) if not is_reset_password else password_reset_token.make_token(user),
    })

    send_email_verification.delay(mail_message, email, mail_subject)
