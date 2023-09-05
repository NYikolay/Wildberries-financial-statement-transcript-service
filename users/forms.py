from gettext import ngettext

from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, validate_email

from users.models import User, WBApiKey, TaxRate, NetCost


class LoginForm(forms.Form):
    email = forms.EmailField(required=True, validators=[validate_email])
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class UserRegisterForm(UserCreationForm):
    is_accepted_terms_of_offer = forms.BooleanField(
        error_messages={'required': 'Необходимо согласие с условиями Оферты'},
        required=True)

    class Meta:
        model = User
        fields = ["email", 'is_accepted_terms_of_offer', 'phone', "password1", "password2"]
        
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields["promocode"] = forms.CharField(required=False)


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(required=True, validators=[validate_email])


class UserPasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Введите пароль",
                "class": 'password_reset-input'
            }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Повторите пароль",
                "class": 'password_reset-input'
            }),
    )


class APIKeyForm(forms.ModelForm):
    class Meta:
        model = WBApiKey
        fields = ["api_key", "name"]
        widgets = {
            'api_key': forms.Textarea(attrs={
                'class': 'api_key-input',
                'cols': 3,
                'rows': 2
            }),
            'name': forms.TextInput(attrs={
                'class': 'shop_name-input'
            }),
        }


class UpdateAPIKeyForm(forms.ModelForm):

    class Meta:
        model = WBApiKey
        fields = ["api_key", "name"]


class TaxRateForm(forms.ModelForm):
    class Meta:
        model = TaxRate
        fields = ["tax_rate", "commencement_date"]


class NetCostForm(forms.ModelForm):
    class Meta:
        model = NetCost
        fields = ["amount", "cost_date"]


class ChangeUserDataForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ChangeUserPasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    reenter_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean(self):
        if len(self.cleaned_data['new_password']) < 8:
            raise ValidationError(
                ngettext(
                    "Пароль должен содержать минимум %(min_length)d символов.",
                    "Пароль должен содержать минимум %(min_length)d символов.",
                    8
                ),
                code='password_too_short',
                params={'min_length': 8},
            )

        if self.cleaned_data['new_password'] != self.cleaned_data['reenter_password']:
            raise ValidationError('Пароли не совпадают!')

        return self.cleaned_data


class LoadNetCostsFileForm(forms.Form):
    net_costs_file = forms.FileField(label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'file-load_input'

    def clean_net_costs_file(self):
        if self.cleaned_data['net_costs_file'].name.lower().split('.')[-1] != 'xlsx':
            raise ValidationError('Расширение загружаемого файла должно быть xlsx!')
        return self.cleaned_data


class ExcelNetCostsForm(forms.Form):
    nm_id = forms.IntegerField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    cost_date = forms.DateField()






