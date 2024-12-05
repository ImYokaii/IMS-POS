import os
from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from .models import QuotationSubmission, QuotationSubmissionItem, PurchaseInvoice
from procurement_view.models import PurchaseOrder
from dotenv import load_dotenv

load_dotenv()

# Create a button Approved or Rejected if the status is Pending.
# Create a button Delivered if the status is Approved.
class PurchaseOrderStatusForm(forms.ModelForm):
    class Meta:
        STATUS_CHOICES = [(status, status) for status in os.environ.get('PO_STATUS_CHOICES', '').split(',')]

        model = PurchaseOrder
        fields = ['status']

        widgets = {
            'status': forms.Select(choices=STATUS_CHOICES),
        }


class QuotationSubmissionForm(forms.ModelForm):
    USER_ROLE = os.environ.get('ROLE_3')

    supplier = forms.ModelChoiceField(queryset=User.objects.filter(userpermission__role=USER_ROLE), label=USER_ROLE)
    
    class Meta:
        model = QuotationSubmission
        fields = [
            'supplier', 'buyer_company_name', 'buyer_address', 'buyer_contact', 
            'quotation_no', 'prepared_by', 'quote_valid_until',  
            'terms_and_conditions'
        ]
        
        widgets = {
            'quote_valid_until': forms.DateInput(attrs={'type': 'date'}),
            'date_submitted': forms.DateInput(attrs={'type': 'date'}),
        }


class QuotationSubmissionItemForm(forms.ModelForm):
    class Meta:
        model = QuotationSubmissionItem
        fields = ['product_name', 'quantity', 'unit_price']

QuotationSubmissionItemFormSet = modelformset_factory(QuotationSubmissionItem, form=QuotationSubmissionItemForm, extra=5)


class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        fields = ['supplier', 'supplier_company_name', 'supplier_address', 'status']