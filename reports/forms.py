from django import forms

from users.models import NetCost, SaleReport


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


class QueryFiltersForm(forms.Form):
    subject_name = forms.CharField(required=False)
    brand_name = forms.CharField(required=False)
    year = forms.ChoiceField(choices=[(str(y), str(y)) for y in range(2020, 2030)], required=False)
    week_numbers = forms.CharField(required=False)

    def clean_week_numbers(self):
        week_numbers = self.cleaned_data.get('week_numbers', '')
        return [int(num) for num in week_numbers.split(',')]
