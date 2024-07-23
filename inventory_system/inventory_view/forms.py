from django import forms
from .models import Product

class PerishableProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'sku', 'category', 'price', 'cost_price',
            'quantity_in_stock', 'unit_of_measurement', 'weight', 'dimensions',
            'color', 'material', 'supplier_name', 'supplier_contact', 'reorder_level',
            'last_restock_date', 'warranty_period', 'expiration_date', 'batch_number', 'brand'
        ]
        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'last_restock_date': forms.DateInput(attrs={'type': 'date'}),
        }

class NonPerishableProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'sku', 'category', 'price', 'cost_price',
            'quantity_in_stock', 'unit_of_measurement', 'weight', 'dimensions',
            'color', 'material', 'supplier_name', 'supplier_contact', 'reorder_level',
            'last_restock_date', 'warranty_period', 'brand'
        ]
        widgets = {
            'last_restock_date': forms.DateInput(attrs={'type': 'date'}),
        }
