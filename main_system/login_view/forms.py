from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField
from django import forms
from .models import UserPermission, CompanyProfile


# ===== USER LOGIN FORM ===== #
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=255, required=True)
    password = forms.PasswordInput()
    captcha = ReCaptchaField()

    class Meta:
        fields = ['username', 'password', 'captcha']
# =============================================== #


# ===== USER Registration FORM ===== #
class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    captcha = ReCaptchaField()


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'captcha']
# =============================================== #


# ===== SUPPLIER Registration FORM ===== #
class CompanyRegistrationForm(forms.ModelForm):

    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'company_address', 'company_contact']

    company_name = forms.CharField(required=True)
    company_address = forms.CharField(required=True)
    company_contact = forms.CharField(required=True)
# =============================================== #