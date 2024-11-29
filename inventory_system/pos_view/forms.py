from django import forms

class ProductSearchForm(forms.Form):
    sku = forms.CharField(label='Search by SKU', required=False)
    name = forms.CharField(label='Search by Product Name', required=False)