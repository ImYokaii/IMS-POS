from django import forms
from django.contrib.auth.models import User
from login_view.models import CompanyProfile
from django.core.exceptions import ValidationError


class UserProfileForm(forms.ModelForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, required=True, label="Current Password", min_length=8)
    new_password = forms.CharField(widget=forms.PasswordInput, required=True, label="New Password", min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm New Password", min_length=8)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise ValidationError('The new password and confirmation do not match.')

        return cleaned_data


class CompanyProfileForm(forms.ModelForm):
    company_name = forms.CharField(required=True)
    company_address = forms.CharField(required=True)
    company_contact = forms.CharField(required=True)

    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'company_address', 'company_contact']