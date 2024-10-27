from django import forms
from django.forms import modelformset_factory
from .models import RequestQuotation, RequestQuotationItem, QuotationSubmission, QuotationSubmissionItem

class RequestQuotationForm(forms.ModelForm):
    class Meta:
        STATUS_CHOICES = [('Ongoing', 'Ongoing'), ('Ended', 'Ended')]
        
        model = RequestQuotation
        
        fields = ['employee', 'buyer_company_name', 'buyer_address', 'buyer_contact', 'quotation_no', 'prepared_by', 'quote_valid_until',
                'terms_and_conditions', 'status',]
        
        widgets = {
            'quote_valid_until': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=STATUS_CHOICES),
        }

class RequestQuotationItemForm(forms.ModelForm):
    class Meta:
        model = RequestQuotationItem
        fields = ['product_name', 'quantity', 'unit_price']

RequestQuotationItemFormSet = modelformset_factory(RequestQuotationItem, form=RequestQuotationItemForm, extra=5)

class QuotationSubmissionForm(forms.ModelForm):
    class Meta:
        STATUS_CHOICES = [('Accept', 'Accept'), ('Pending', 'Pending')]

        model = QuotationSubmission
        fields = [
            'supplier', 'buyer_company_name', 'buyer_address', 'buyer_contact', 
            'quotation_no', 'prepared_by', 'quote_valid_until',  
            'terms_and_conditions', 'total_amount', 'status'
        ]
        
        widgets = {
            'quote_valid_until': forms.DateInput(attrs={'type': 'date'}),
            'date_submitted': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=STATUS_CHOICES),
        }

class QuotationSubmissionItemForm(forms.ModelForm):
    class Meta:
        model = QuotationSubmissionItem
        fields = ['product_name', 'quantity', 'unit_price']

QuotationSubmissionItemFormSet = modelformset_factory(
    QuotationSubmissionItem,
    form=QuotationSubmissionItemForm,
    extra=5  # Adjust the number of extra forms as needed
)