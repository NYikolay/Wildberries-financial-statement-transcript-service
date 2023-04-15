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

