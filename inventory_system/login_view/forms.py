from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField
from django import forms
from .models import UserPermission, Supplier


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
class SupplierRegistrationForm(forms.ModelForm):
    """Form to register a supplier with specific details."""
    class Meta:
        model = Supplier
        fields = ['supplier_company_name', 'supplier_company_address', 'supplier_company_contact']
# =============================================== #