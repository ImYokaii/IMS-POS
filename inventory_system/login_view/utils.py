import os
from dotenv import load_dotenv
from django.core.cache import cache
from django.shortcuts import render, HttpResponse, redirect


load_dotenv()


# ===== CHECK USER'S ROLE AFTER LOGIN ===== #
def check_logging_user_role(role):
    ROLE_3_URL = os.environ.get('ROLE_3_URL').split(",")

    if role == os.environ.get('ROLE_1'):
        return "managers" # dummy page message
    
    elif role == os.environ.get('ROLE_2'):
        return "employees" # dummy page message
    
    elif role == os.environ.get('ROLE_3'):
        return ROLE_3_URL[0]
    
    else:
        return "unknowns"
# =============================================== #
    

# ===== GET CLIENT IP FOR LOGIN ATTEMPTS ===== #
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]

    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip
# =============================================== #


# ===== CHECK FOR NUMBER OF FAILED LOGIN ATTEMPTS ===== #
def increment_failed_login_attempts(request, username):
    ip = get_client_ip(request)
    lock_duration = int(os.environ.get('FAILED_LOGIN_LOCK_DURATION'))
    max_attempts = int(os.environ.get('MAX_FAILED_LOGIN_ATTEMPTS'))

    if ip:
        key_ip = f'failed_login_attempts_{ip}'
        attempts_ip = cache.get(key_ip, 0) + 1
        cache.set(key_ip, attempts_ip, timeout=lock_duration)

        if attempts_ip >= max_attempts:
            return HttpResponse("Temporarily locked due to multiple failed login attempts. Wait for 60 seconds")

    if username:
        key_user = f'failed_login_attempts_{username}'
        attempts_user = cache.get(key_user, 0) + 1
        cache.set(key_user, attempts_user, timeout=lock_duration)

    return None
# =============================================== #