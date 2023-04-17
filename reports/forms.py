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
    report_data_file = forms.FileField(label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'file-load_input'

    def clean_report_data_file(self):
        if self.cleaned_data['report_data_file'].name.lower().split('.')[-1] != 'xlsx':
            raise ValidationError('Расширение загружаемого файла должно быть xlsx!')
        return self.cleaned_data


