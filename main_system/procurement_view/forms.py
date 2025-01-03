import os
from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from .models import RequestQuotation, RequestQuotationItem, PurchaseOrder, PurchaseOrderItem
from supplier_view.models import PurchaseInvoice
from inventory_view.models import Product
from dotenv import load_dotenv

load_dotenv()


class RequestQuotationForm(forms.ModelForm):
    class Meta:
        model = RequestQuotation
        
        fields = ['buyer_contact', 'quote_valid_until',
                'terms_and_conditions',]
        
        widgets = {
            'quote_valid_until': forms.DateInput(attrs={'type': 'date'})
        }

class RequestQuotationItemForm(forms.ModelForm):
    class Meta:
        model = RequestQuotationItem

        fields = ['product_name', 'quantity', 'unit_price', 'measurement', 'price_valid_until']

        widgets = {
            'price_valid_until': forms.DateInput(attrs={'type': 'date'})
        }

    product_name = forms.ChoiceField(
        choices=[('', '--- Select Existing Product ---')] +
                [(product.name, product.name) for product in Product.objects.all()],
        required=False,
        label='Existing Product'
    )

    other_product_name = forms.CharField(max_length=255, required=False, label='Other Product Name', widget=forms.TextInput(attrs={'placeholder': 'Enter custom product name if not in list'}))

RequestQuotationItemFormSet = modelformset_factory(RequestQuotationItem, form=RequestQuotationItemForm, extra=5)


class EditQuotationPriceForm(forms.ModelForm):
    class Meta:
        model = RequestQuotationItem
        fields = ['unit_price', 'price_valid_until']

        widgets = {
            'price_valid_until': forms.DateInput(attrs={'type': 'date'})
        }


class PurchaseOrderForm(forms.ModelForm):
    deliver_date = forms.Form()

    class Meta:
        STATUS_CHOICES = [(status, status) for status in os.environ.get('PO_STATUS_CHOICES', '').split(',')]
        
        model = PurchaseOrder

        fields = [
            'buyer_contact', 'delivery_date', 'notes'
        ]
        
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=STATUS_CHOICES),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product_name', 'quantity', 'unit_price']

    product_name = forms.ChoiceField(
        choices=[('', '--- Select Existing Product ---')] + 
                [(product.name, product.name) for product in Product.objects.all()],
        required=False,
        label='Existing Product'
    )
    
    other_product_name = forms.CharField(max_length=255, required=False, label='Other Product Name', widget=forms.TextInput(attrs={'placeholder': 'Enter custom product name if not in list'})
)

PurchaseOrderItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=5)


class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        STATUS_CHOICES = [(status, status) for status in os.environ.get('PI_STATUS_CHOICES', '').split(',')]

        model = PurchaseInvoice

        fields = ['status']

        widgets = {
            'status': forms.Select(choices=STATUS_CHOICES),
        }