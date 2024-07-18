import os
from dotenv import load_dotenv
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm
from .models import UserPermission

load_dotenv()


# ===== GET CLIENT IP FOR LOGIN ATTEMPTS ===== #
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]

    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip
# =============================================== #


# ===== LOGIN PAGE ===== #
def login_page(request):
    if request.user.is_authenticated:
        return HttpResponse("Welcome")
    
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Reset failed login attempts for this IP and username upon successful login
                ip = get_client_ip(request)
                if ip:
                    cache.delete(f'failed_login_attempts_{ip}')
                cache.delete(f'failed_login_attempts_{username}')
        

                permission = UserPermission.objects.get(user=user)
                if permission.role == os.environ.get('ROLE_1'):
                    return HttpResponse("Hi Manager")
                
                elif permission.role == os.environ.get('ROLE_2'):
                    return HttpResponse("Hi Employee")
                
                elif permission.role == os.environ.get('ROLE_3'):
                    return HttpResponse("Hi Supplier")
                
                else:
                    return HttpResponse("Wait for role permission")
            
        else:
            # Increment failed login attempts for this IP
            ip = get_client_ip(request)
            if ip:
                key = f'failed_login_attempts_{ip}'
                attempts = cache.get(key, 0)
                attempts += 1
                cache.set(key, attempts, timeout=int(os.environ.get('FAILED_LOGIN_LOCK_DURATION')))
                
                if attempts >= int(os.environ.get('MAX_FAILED_LOGIN_ATTEMPTS')):
                    return HttpResponse("Temporarily locked due to multiple failed login attempts. Wait for 60 seconds")
                
            username = request.POST.get('username')
            if username:
                key_user = f'failed_login_attempts_{username}'
                attempts_user = cache.get(key_user, 0) + 1
                cache.set(key_user, attempts_user, timeout=int(os.environ.get('FAILED_LOGIN_LOCK_DURATION')))

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
# =============================================== #