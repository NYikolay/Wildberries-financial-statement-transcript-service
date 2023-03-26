from django import forms

from config.settings.base import IS_TEST_MODE, ROBOKASSA_CULTURE, ROBOKASSA_PASSWORD1, \
    ROBOKASSA_PASSWORD2
from payments.models import SuccessPaymentNotification, SubscriptionTypes
from payments.services.check_signature_result import check_signature_result


class RoboKassaForm(forms.Form):
    OutSum = forms.DecimalField(min_value=0, max_digits=15, decimal_places=2, required=True)
    Description = forms.CharField(max_length=100, required=True)
    CustomerEmail = forms.CharField(max_length=100, required=True)
    UserEmail = forms.CharField(max_length=100, required=True)
    Culture = forms.CharField(max_length=10, initial=ROBOKASSA_CULTURE)
    SubscriptionType = forms.ChoiceField(choices=SubscriptionTypes.choices)
    Discount = forms.DecimalField(min_value=0, max_digits=4, decimal_places=2)
    Duration = forms.IntegerField(min_value=1)
    DurationDescription = forms.CharField(max_length=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['IsTest'] = forms.IntegerField(required=False)
        self.fields['IsTest'].initial = 1 if IS_TEST_MODE else 0

        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()


class ResultURLForm(forms.Form):
    OutSum = forms.DecimalField(min_value=0, max_digits=15, decimal_places=2)
    InvId = forms.IntegerField(min_value=0)
    SignatureValue = forms.CharField(max_length=32)
    Shp_discount = forms.DecimalField(min_value=0, max_digits=4, decimal_places=2)
    Shp_duration = forms.IntegerField(min_value=1)
    Shp_durationdesc = forms.CharField(max_length=10)
    Shp_type = forms.ChoiceField(choices=SubscriptionTypes.choices)
    Shp_user = forms.EmailField()

    def clean(self):
        try:
            check_status = check_signature_result(
                self.cleaned_data['InvId'],
                self.cleaned_data['OutSum'],
                self.cleaned_data['SignatureValue'],
                ROBOKASSA_PASSWORD2,
                self.cleaned_data['Shp_discount'],
                self.cleaned_data['Shp_duration'],
                self.cleaned_data['Shp_durationdesc'],
                self.cleaned_data['Shp_type'],
                self.cleaned_data['Shp_user']
            )

            if not check_status:
                raise forms.ValidationError('Ошибка в контрольной сумме')
        except KeyError:
            raise forms.ValidationError('Пришли не все необходимые параметры')

        return self.cleaned_data


class SuccessRedirectForm(ResultURLForm):

    def clean(self):
        try:
            check_status = check_signature_result(
                self.cleaned_data['InvId'],
                self.cleaned_data['OutSum'],
                self.cleaned_data['SignatureValue'],
                ROBOKASSA_PASSWORD1,
                self.cleaned_data['Shp_discount'],
                self.cleaned_data['Shp_duration'],
                self.cleaned_data['Shp_durationdesc'],
                self.cleaned_data['Shp_type'],
                self.cleaned_data['Shp_user']
            )

            if not check_status:
                raise forms.ValidationError('Ошибка в контрольной сумме')
        except KeyError:
            raise forms.ValidationError('Пришли не все необходимые параметры')

        if not SuccessPaymentNotification.objects.filter(inv_id=self.cleaned_data['InvId']):
            raise forms.ValidationError('От ROBOKASSA не было предварительного уведомления')

        return self.cleaned_data


class FailRedirectForm(forms.Form):
    OutSum = forms.DecimalField(min_value=0, max_digits=15, decimal_places=2)
    InvId = forms.IntegerField(min_value=0)
    Culture = forms.CharField(max_length=10)


