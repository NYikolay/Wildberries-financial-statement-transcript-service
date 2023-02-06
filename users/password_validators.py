import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class LengthValidator:
    def __init__(self, length=8,):
        self.length = length

    def validate(self, password, user=None):
        if len(password) < self.length:
            raise ValidationError(
                _("Пароль должен содержать минимум %(length)d символов."),
                code='password_should_6_digits_pin',
                params={'length': self.length},
            )

    def get_help_text(self):
        return ''

