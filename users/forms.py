from gettext import ngettext

from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, validate_email
from django.utils.translation import gettext_lazy as _

from users.models import User, WBApiKey, TaxRate, NetCost, Promocode, SaleReport


class LoginForm(forms.Form):
    use_required_attribute = False
    email = forms.EmailField(
        required=True,
        error_messages={"invalid": _("Введён некорректный адресс электронной почты")},
        widget=forms.TextInput(attrs={
            'class': "form__input",
            'id': 'email',
            'placeholder': 'support_commery@mail.ru',
            'data-id': 'email'
        }))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': "form__input",
                'data-id': 'password',
                'id': 'password',
            }
        ),
        label="Пароль",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    def clean_email(self):
        email = self.cleaned_data['email']

        validate_email(email)

        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email or not password:
            return

        user = User.objects.filter(email__iexact=email).first()

        if not user:
            self.add_error("email", "Введён неверный Email")
            return
        elif not user.check_password(password):
            self.add_error("password", "Введён неверный пароль")
            return
        else:
            self.cleaned_data['user'] = user


class UserRegisterForm(UserCreationForm):
    use_required_attribute = False
    is_accepted_terms_of_offer = forms.BooleanField(
        error_messages={'required': 'Необходимо согласие с условиями Оферты'},
        widget=forms.CheckboxInput(attrs={'data-id': 'is_accepted_terms_of_offer'}),
        label='Принять условия Оферты',
        required=True,
        initial=True
    )
    password1 = forms.CharField(
        error_messages={'required': 'Пароль обязателен для заполнения'},
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'password1', 'id': 'password1'}),
        label='Пароль',
        required=True
    )
    password2 = forms.CharField(
        error_messages={'required': 'Необходимо повторить пароль'},
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'password2', 'id': 'password2'}),
        label='Повторить пароль',
        required=True
    )

    class Meta:
        model = User
        fields = ["email", 'is_accepted_terms_of_offer', 'phone', "password1", "password2"]
        labels = {
            'password2': _('Подтвердить пароль'),
            'phone': _('Контактный телефон')
        }
        widgets = {
            'email': forms.TextInput(attrs={
                'class': "form__input",
                'placeholder': 'support_commery@mail.ru',
                'data-id': 'email',
                'id': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': "form__input",
                'placeholder': '8 (977) 438-99-99',
                'data-id': 'phone',
                'id': 'phone'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["promocode"] = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': 'HXTYUUU1',
            'data-id': 'promocode'
        }), label='Промокод')

    def clean_email(self):
        email = self.cleaned_data['email']

        validate_email(email)

        return email

    def clean(self):
        cleaned_data = super().clean()
        promo_code_value = cleaned_data.get('promocode')

        if promo_code_value:
            promo_code = Promocode.objects.filter(value=promo_code_value).first()

            if not promo_code:
                self.add_error('promocode', 'Указанный промокод не существует')
                return
            else:
                self.cleaned_data['promo_code'] = promo_code


class PasswordResetEmailForm(forms.Form):
    use_required_attribute = False
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': "form__input",
            'placeholder': 'support_commery@mail.ru',
            'data-id': 'email',
            'id': 'email'
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    def clean_email(self):
        email = self.cleaned_data['email']

        validate_email(email)

        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if not email:
            return

        user = User.objects.filter(email=email).first()

        if not user:
            self.add_error("email", "Аккаунта с такой почтой не существует")
            return
        else:
            self.cleaned_data['user'] = user


class UserPasswordResetForm(SetPasswordForm):
    use_required_attribute = False
    new_password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'new_password1'}),
        required=True
    )
    new_password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'new_password2'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""


class TaxRateForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = TaxRate
        fields = ["tax_rate", "commencement_date"]
        labels = {
            "tax_rate": "Ставка",
            "commencement_date": "Дата начала действия"
        }
        widgets = {
            "tax_rate": forms.NumberInput(attrs={
                'class': 'form__input',
                'data-id': 'tax_rate',
                'id': 'tax_rate',
                'max': 100,
                'step': '0.01',
                'min': 0,
            }),
            'commencement_date': forms.DateInput(format='%Y-%m-%d', attrs={
                "class": 'form__input',
                'data-id': 'commencement_date',
                'id': 'commencement_date',
                'type': 'date',
            })
        }

    def clean_tax_rate(self):
        tax_rate = self.cleaned_data['tax_rate']

        if tax_rate > 100:
            raise ValidationError("Значение налога не может быть более 100%")

        return tax_rate

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""


class CostsForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = SaleReport
        fields = ["supplier_costs"]
        widgets = {
            "supplier_costs": forms.NumberInput(attrs={
                'class': 'form__input costs-input',
                'id': 'supplier_costs',
                'min': 0,
            })
        }


class APIKeyForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = WBApiKey
        fields = ["api_key", "name"]
        labels = {
            'api_key': 'API-ключ “Статистика”',
            'name': 'Название подключения'
        }
        widgets = {
            'api_key': forms.Textarea(attrs={
                'class': 'form__input',
                'cols': 1,
                'rows': 10,
                'data-id': 'api_key',
                'style': 'resize:none;',
                'id': 'api_key'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form__input',
                'data-id': 'name',
                'id': 'name'
            }),
        }
        error_messages = {
            'api_key': {
                'required': _("Необходим API-ключ"),
            },
            'name': {
                'required': _("Введите название подключения"),
            },
        }

    def __init__(self, *args, **kwargs):
        self.api_keys_count = kwargs.pop('api_keys_count', None)
        self.label_suffix = ""
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.api_keys_count and self.api_keys_count >= 10:
            self.add_error("api_key", "Нельзя создать более 10 подключений к WILDBERRIES по API")


class ChangeCurrentApiKeyForm(forms.Form):
    api_key_id = forms.IntegerField()


class UpdateAPIKeyForm(forms.ModelForm):

    class Meta:
        model = WBApiKey
        fields = ["api_key", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""


class ChangeUserPasswordForm(forms.Form):
    use_required_attribute = False
    old_password = forms.CharField(
        label='Старый пароль',
        error_messages={'required': 'Старый пароль обязателен к заполнению'},
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'old_password'}),
        required=True
    )
    new_password = forms.CharField(
        label='Новый пароль',
        error_messages={'required': 'Пароль обязателен к заполнению'},
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'new_password'}),
        required=True
    )
    reenter_password = forms.CharField(
        label='Повтор нового пароля',
        error_messages={'required': 'Необходимо повторить пароль'},
        widget=forms.PasswordInput(attrs={'class': "form__input", 'data-id': 'reenter_password'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.label_suffix = ""
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        old_password = cleaned_data.get('old_password')
        reenter_password = cleaned_data.get('reenter_password')

        if not new_password or not old_password or not reenter_password:
            return

        if len(new_password) < 8:
            self.add_error("new_password", "Пароль должен содержать минимум 8 символов.")
            return

        if new_password != self.cleaned_data['reenter_password']:
            self.add_error("reenter_password", "Пароли не совпадают.")
            return

        if not self.user.check_password(cleaned_data['old_password']):
            self.add_error("old_password", "Старый пароль введён неверно.")
            return


class LoadNetCostsFileForm(forms.Form):
    net_costs_file = forms.FileField(
        label='',
        widget=forms.FileInput(attrs={'class': 'common__load-input', 'id': 'file-input'}),
        required=True
    )

    def clean_net_costs_file(self):
        if self.cleaned_data['net_costs_file'].name.lower().split('.')[-1] != 'xlsx':
            raise ValidationError('Расширение загружаемого файла должно быть xlsx!')
        return self.cleaned_data


class NetCostForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = NetCost
        fields = ["product", "amount", "cost_date"]
        labels = {
            "amount": "Себестоимость",
            "cost_date": "Дата начала действия"
        }
        error_messages = {
            "amount": {
                "required": _("Значение себестоимости обязательно для заполнения")
            },
            "cost_date": {
                "required": _("Необходимо указать дату начала действия себестоимости")
            }
        }
        widgets = {
            "amount": forms.NumberInput(attrs={
                'class': 'form__input net__cost-input',
                'data-id': 'amount',
                'id': 'amount',
                'min': 0,
            }),
            'cost_date': forms.DateInput(format='%Y-%m-%d', attrs={
                "class": 'form__input net__cost-input',
                'data-id': 'cost_date',
                'id': 'cost_date',
                'type': 'date',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""


class ExcelNetCostsForm(forms.Form):
    nm_id = forms.IntegerField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    cost_date = forms.DateField()






