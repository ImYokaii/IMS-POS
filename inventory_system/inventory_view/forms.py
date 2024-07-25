import os
from dotenv import load_dotenv
from django import forms
from .models import Product

load_dotenv()

CATEGORY_CHOICES = [
    ('Concreting and Masonry', 'Concreting and Masonry'),
    ('Rebars and Gi Wires', 'Rebars and Gi Wires'),
    ('Roofing and Insulation', 'Roofing and Insulation'),
    ('Steel', 'Steel'),
    ('Water Proofing', 'Water Proofing'),
    ('Sealant and Adhesive', 'Sealant and Adhesive'),
    ('Wood Products', 'Wood Products'),
    ('Dry Wall and Ceiling', 'Dry Wall and Ceiling'),
    ('Plumbing Pipes', 'Plumbing Pipes'),
    ('Electrical Pipes', 'Electrical Pipes'),
    ('Wires and Cables', 'Wires and Cables'),
    ('Tiling Supplies', 'Tiling Supplies'),
    ('Painting Supplies', 'Painting Supplies'),
    ('Door and Cabinet Hardwares', 'Door and Cabinet Hardwares'),
    ('Electrical Fixtures and Devices', 'Electrical Fixtures and Devices'),
    ('Finishing Materials', 'Finishing Materials'),
    ('Power Tools and Equipments', 'Power Tools and Equipments'),
    ('Nails and Screws', 'Nails and Screws'),
    ('Screen and Covers', 'Screen and Covers'),
    ('Chemicals', 'Chemicals'),
]

PRODUCT_CATEGORIES = os.environ.get('PRODUCT_CATEGORIES', '').split(',')
PRODUCT_TYPES = os.environ.get('PRODUCT_TYPES', '').split(',')


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
            'category': forms.Select(choices=CATEGORY_CHOICES),
        }


class NonPerishableProductForm(forms.ModelForm):
    category = forms.Select(choices=CATEGORY_CHOICES)

    class Meta:
        model = Product

        fields = [
            'name', 'description', 'sku', 'category', 'price', 'cost_price', 
            'unit_of_measurement', 'weight', 'dimensions', 'color', 'material', 
            'supplier_name', 'brand'
        ]

        widgets = {
            'category': forms.Select(choices=CATEGORY_CHOICES),
        }


class ProductFilterForm(forms.Form):
    sku = forms.CharField(max_length=50, required=False)
    name = forms.CharField(max_length=100, required=False)
    product_type = forms.ChoiceField(choices=[("", "All Products")] + [(ptype, ptype) for ptype in PRODUCT_TYPES], required=False)
    category = forms.ChoiceField(choices=[("", "All Categories")] + [(category, category) for category in PRODUCT_CATEGORIES], required=False)
    expiration_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))



