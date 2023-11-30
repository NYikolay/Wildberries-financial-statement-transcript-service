import json

from django import forms

from users.models import NetCost, SaleReport
from django.core.exceptions import ValidationError


class SaleReportForm(forms.ModelForm):

    class Meta:
        model = SaleReport
        fields = ['storage_cost', 'cost_paid_acceptance', 'other_deductions', 'supplier_costs']
        widgets = {
            'storage_cost': forms.NumberInput(attrs={
                'class': 'report_input-item',
            }),
            'cost_paid_acceptance': forms.NumberInput(attrs={
                'class': 'report_input-item',
            }),
            'other_deductions': forms.NumberInput(attrs={
                'class': 'report_input-item',
            }),
            'supplier_costs': forms.NumberInput(attrs={
                'class': 'report_input-item'
            }),
        }


class LoadReportAdditionalDataFrom(forms.Form):
    report_data_file = forms.FileField(
        label='',
        widget=forms.FileInput(attrs={'class': 'expenses__load-input', 'id': 'file-input'})
    )

    def clean_report_data_file(self):
        if self.cleaned_data['report_data_file'].name.lower().split('.')[-1] != 'xlsx':
            raise ValidationError('Расширение загружаемого файла должно быть xlsx!')
        return self.cleaned_data


class ReportByBarcodeForm(forms.Form):
    period_filters = forms.CharField()
    nm_id = forms.IntegerField()
    image = forms.URLField()
    product_name = forms.CharField()
    barcode = forms.IntegerField()
    share_in_revenue = forms.FloatField()
    abc_group = forms.CharField(max_length=1)
    xyz_group = forms.CharField(max_length=2)

    def clean_period_filters(self):
        jdata = self.cleaned_data['period_filters']
        try:
            json_data = json.loads(jdata)
        except:
            raise ValidationError("Invalid data in period_filters field")

        return json_data


