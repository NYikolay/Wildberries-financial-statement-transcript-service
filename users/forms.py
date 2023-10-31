from gettext import ngettext

from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, validate_email
from django.utils.translation import gettext_lazy as _

from users.models import User, WBApiKey, TaxRate, NetCost, Promocode


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        validators=[validate_email],
        widget=forms.EmailInput(attrs={
            'class': "form__input",
            'placeholder': 'support_commery@mail.ru',
            'data-id': 'email'
        }))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'password'}),
        label="Пароль",
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data['email']
        password = cleaned_data['password']
        user = User.objects.filter(email=email).first()

        if not user:
            self.add_error("email", "Введён неверный Email")
        elif not user.check_password(password):
            self.add_error("password", "Введён неверный пароль")
        else:
            self.cleaned_data['user'] = user


class UserRegisterForm(UserCreationForm):
    is_accepted_terms_of_offer = forms.BooleanField(
        error_messages={'required': 'Необходимо согласие с условиями Оферты'},
        widget=forms.CheckboxInput(attrs={'data-id': 'is_accepted_terms_of_offer'}),
        label='Принять условия Оферты',
        required=True)
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'password1'}),
        label='Пароль'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'password2'}),
        label='Повторить пароль'
    )

    class Meta:
        model = User
        fields = ["email", 'is_accepted_terms_of_offer', 'phone', "password1", "password2"]
        labels = {
            'password2': _('Подтвердить пароль'),
            'phone': _('Контактный телефон')
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': "form__input",
                'placeholder': 'support_commery@mail.ru',
                'data-id': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': "form__input",
                'placeholder': '8 (977) 438-99-99',
                'data-id': 'phone'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields["promocode"] = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': 'HXTYUUU1',
            'data-id': 'promocode'
        }), label='Промокод')

    def clean(self):
        cleaned_data = super().clean()
        promo_code_value = cleaned_data['promocode']

        if promo_code_value:
            promo_code = Promocode.objects.filter(value=promo_code_value).first()

            if not promo_code:
                self.add_error('promocode', 'Указанный промокод не существует')
            else:
                self.cleaned_data['promo_code'] = promo_code


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        validators=[validate_email],
        widget=forms.EmailInput(attrs={
            'class': "form__input",
            'placeholder': 'support_commery@mail.ru',
            'data-id': 'email'
        }))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data['email']
        user = User.objects.filter(email=email).first()

        if not user:
            self.add_error("email", "Аккаунта с такой почтой не существует")
        else:
            self.cleaned_data['user'] = user


class UserPasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'new_password1'}),
    )
    new_password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'new_password2'})
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
    old_password = forms.CharField(
        label='Старый пароль',
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'old_password'}),
        required=True
    )
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'new_password'}),
        required=True
    )
    reenter_password = forms.CharField(
        label='Повтор нового пароля',
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'reenter_password'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data['new_password']

        if len(new_password) < 8:
            self.add_error("new_password", "Пароль должен содержать минимум 8 символов.")

        if new_password != self.cleaned_data['reenter_password']:
            self.add_error("reenter_password", "Пароли не совпадают.")

        if not self.user.check_password(cleaned_data['old_password']):
            self.add_error("old_password", "Старый пароль введён неверно.")


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






