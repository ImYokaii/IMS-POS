from django import forms
from django.contrib.auth.models import User
from login_view.models import Supplier

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class SupplierProfileForm(forms.ModelForm):
    supplier_company_name = forms.CharField(required=True)
    supplier_company_address = forms.CharField(required=True)
    supplier_company_contact = forms.CharField(required=True)

    class Meta:
        model = Supplier
        fields = ['supplier_company_name', 'supplier_company_address', 'supplier_company_contact']