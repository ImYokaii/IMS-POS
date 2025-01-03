import os
from dotenv import load_dotenv
from django import forms
from django.forms import DateField
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


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            'name', 'category', 'quantity', 'measurement', 'reorder_level', 'selling_price', 'cost_price'
        ]

        widgets = {
            'category': forms.Select(choices=CATEGORY_CHOICES),
        }


class RestockProductForm(forms.Form):
    quantity = forms.IntegerField(required=True, min_value=1)


class WasteProductForm(forms.Form):
    quantity = forms.IntegerField(required=True, min_value=1)
    reason = forms.CharField(required=True)


class ProductFilterForm(forms.Form):
    sku = forms.CharField(max_length=50, required=False)
    name = forms.CharField(max_length=100, required=False)
    category = forms.ChoiceField(choices=[(category, category) for category in PRODUCT_CATEGORIES], required=False)


class WasteProductFilterForm(forms.Form):
    sku = forms.CharField(required=False)
    name = forms.CharField(required=False)
    category = forms.ChoiceField(choices=[(category, category) for category in PRODUCT_CATEGORIES], required=False)
    date_wasted = forms.DateField(required=False)


class EditProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = ['name', 'category', 'measurement', 'reorder_level', 'selling_price', 'cost_price']

        widgets = {
            'category': forms.Select(choices=CATEGORY_CHOICES),
        }

    name = forms.CharField(required=True)
    measurement = forms.CharField(required=True)
    reorder_level = forms.IntegerField(required=True)
    selling_price = forms.IntegerField(required=True)
    cost_price = forms.IntegerField(required=True)
        
