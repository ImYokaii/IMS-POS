from django import forms
from .models import Product

class PerishableProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            'name', 'description', 'sku', 'category', 'price', 'cost_price', 
            'unit_of_measurement', 'weight', 'dimensions', 'color', 'material', 
            'supplier_name', 'expiration_date', 'batch_number', 'brand'
        ]

        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }


class NonPerishableProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            'name', 'description', 'sku', 'category', 'price', 'cost_price', 
            'unit_of_measurement', 'weight', 'dimensions', 'color', 'material', 
            'supplier_name', 'brand'
        ]


class ProductFilterForm(forms.Form):
    sku = forms.CharField(max_length=50, required=False)
    name = forms.CharField(max_length=100, required=False)
    expiration_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))

