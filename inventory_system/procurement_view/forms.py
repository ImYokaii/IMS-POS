from django import forms
from .models import RequestQuotation

class RequestQuotationForm(forms.ModelForm):
    class Meta:
        model = RequestQuotation
        fields = ['employee', 'buyer_company_name', 'buyer_address', 'buyer_contact', 'quotation_no', 'prepared_by', 'quote_valid_until',
                'terms_and_conditions', 'total_amount', 'status',]
        widgets = {
            'quote_valid_until': forms.DateInput(attrs={'type': 'date'}),
        }