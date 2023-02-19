from gettext import ngettext

from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, validate_email

from support.models import ContactMessage
from users.models import User


class SupportRequestForm(forms.ModelForm):

    class Meta:
        model = ContactMessage
        fields = '__all__'
