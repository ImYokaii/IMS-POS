from django import forms
from django.contrib.auth.models import User
from login_view.models import CompanyProfile

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class CompanyProfileForm(forms.ModelForm):
    company_name = forms.CharField(required=True)
    company_address = forms.CharField(required=True)
    company_contact = forms.CharField(required=True)

    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'company_address', 'company_contact']