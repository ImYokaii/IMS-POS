import os
from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from .models import RequestQuotation, RequestQuotationItem, PurchaseOrder, PurchaseOrderItem
from supplier_view.models import PurchaseInvoice
from dotenv import load_dotenv

load_dotenv()


class RequestQuotationForm(forms.ModelForm):
    USER_ROLE = os.environ.get('ROLE_2')

    employee = forms.ModelChoiceField(queryset=User.objects.filter(userpermission__role=USER_ROLE), label=USER_ROLE)

    class Meta:
        STATUS_CHOICES = [(status, status) for status in os.environ.get('RQ_STATUS_CHOICES', '').split(',')]
        
        model = RequestQuotation
        
        fields = ['employee', 'buyer_company_name', 'buyer_address', 'buyer_contact', 'prepared_by', 'quote_valid_until',
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



class PurchaseOrderForm(forms.ModelForm):
    USER_ROLE = os.environ.get('ROLE_3')

    supplier = forms.ModelChoiceField(queryset=User.objects.filter(userpermission__role=USER_ROLE), label=USER_ROLE)

    class Meta:
        STATUS_CHOICES = [(status, status) for status in os.environ.get('PO_STATUS_CHOICES', '').split(',')]
        
        model = PurchaseOrder

        fields = [
            'supplier', 'buyer_company_name', 'buyer_address', 
            'delivery_date', 'notes', 'total_amount', 'approved_by', 'status'
        ]
        
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=STATUS_CHOICES),
        }

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity', 'unit_price']

PurchaseOrderItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=5)


class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        STATUS_CHOICES = [(status, status) for status in os.environ.get('PI_STATUS_CHOICES', '').split(',')]

        model = PurchaseInvoice

        fields = ['status']

        widgets = {
            'status': forms.Select(choices=STATUS_CHOICES),
        }