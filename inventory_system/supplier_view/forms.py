import os
from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from .models import QuotationSubmission, QuotationSubmissionItem, PurchaseInvoice
from procurement_view.models import PurchaseOrder
from dotenv import load_dotenv

load_dotenv()


class QuotationSubmissionForm(forms.ModelForm):
    class Meta:
        model = QuotationSubmission
        fields = [
            'buyer_company_name', 'buyer_address', 'buyer_contact', 
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
        fields = ['product_name', 'quantity', 'unit_price', 'price_valid_until']

        widgets = {
            'price_valid_until': forms.DateInput(attrs={'type': 'date'})
        }

QuotationSubmissionItemFormSet = modelformset_factory(QuotationSubmissionItem, form=QuotationSubmissionItemForm, extra=5)


class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        fields = ['supplier', 'supplier_company_name', 'supplier_address', 'status']