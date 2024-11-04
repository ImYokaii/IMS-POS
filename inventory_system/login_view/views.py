from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm
from .models import UserPermission
from .utils import check_logging_user_role, get_client_ip, increment_failed_login_attempts


# ===== LOGIN PAGE ===== #
def landing_page(Request):
    return HttpResponse("A Landing Page")


# ===== LOGIN PAGE ===== #
def login_page(request):
    if request.user.is_authenticated:
        return HttpResponse("gege")
    
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Reset failed login attempts for user's IP and username upon successful login
                ip = get_client_ip(request)

                if ip:
                    cache.delete(f'failed_login_attempts_{ip}')
                cache.delete(f'failed_login_attempts_{username}')
        

                permission = UserPermission.objects.get(user=user)
                landing_page = check_logging_user_role(permission.role)

                return redirect(landing_page)
            
        else:
            username = request.POST.get('username')
            check_attempts = increment_failed_login_attempts(request, username)

            return redirect("login")
            
    else:
        form = LoginForm()
        return render(request, "login.html", {"form": form})
# =============================================== #


# ===== SIGNUP PAGE ===== #
def signup_page(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("login")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            UserPermission.objects.create(user=user)
            return redirect("login")
        
        else:
            return HttpResponse("Invalid Credentials")
    
    else:
        form = UserRegistrationForm()

    return render(request, "signup.html", {"form": form})
# =============================================== #


# ===== LOGOUT PAGE ===== #
def logout_page(request):
    logout(request)
    
    return HttpResponse("Logged out...")
# =============================================== #


# ===== DUMMY PAGES FOR TESTING ===== #
@login_required(login_url=settings.LOGIN_URL)
def manager_page(request):
    return HttpResponse("You are indeed a Manager!")

@login_required(login_url=settings.LOGIN_URL)
def employee_page(request):
    return HttpResponse("You are indeed an Employee!")

@login_required(login_url=settings.LOGIN_URL)
def supplier_page(request):
    return HttpResponse("You are indeed a Supplier!")

@login_required(login_url=settings.LOGIN_URL)
def unknown_page(request):
    return HttpResponse("You are Unknown...")
# =============================================== #