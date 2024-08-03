import os
from dotenv import load_dotenv
from django import forms
from .models import ProductInstance

load_dotenv()
PRODUCT_CATEGORIES = os.environ.get('PRODUCT_CATEGORIES', '').split(',')

class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = ProductInstance

        fields = ['reorder_level']

class SearchFilterForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    category = forms.ChoiceField(choices=[("", "All Categories")] + [(category, category) for category in PRODUCT_CATEGORIES], required=False)