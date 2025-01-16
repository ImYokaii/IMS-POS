import os
from dotenv import load_dotenv
from django.core.cache import cache
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from datetime import date
from django.utils import timezone


load_dotenv()


# ===== CHECK FOR DUE REQUEST QUOTATIONS AND CHANGE IT'S STATUS ===== #
def check_due_request_quotations():
    from procurement_view.models import RequestQuotation

    RQ_STATUS = os.environ.get('RQ_STATUS_CHOICES').split(',')
    ONGOING_STATUS = RQ_STATUS[0]
    ENDED_STATUS = RQ_STATUS[1]

    today = timezone.now().date()
    today_str = today.strftime('%Y-%m-%d')

    request_quotations = RequestQuotation.objects.filter(quote_valid_until__lte=today_str, status=ONGOING_STATUS)
    request_quotations.update(status=ENDED_STATUS)
# =============================================== #


# ===== CHECK USER'S ROLE AFTER LOGIN ===== #
def check_logging_user_role(role):
    ROLE_1_URL = os.environ.get('ROLE_1_URL').split(",")
    ROLE_2_URL = os.environ.get('ROLE_2_URL').split(",")
    ROLE_3_URL = os.environ.get('ROLE_3_URL').split(",")
    ROLE_4_URL = os.environ.get('ROLE_4_URL').split(",")

    if role == os.environ.get('ROLE_1'):
        check_due_request_quotations()
        return ROLE_1_URL[0]
    
    elif role == os.environ.get('ROLE_2'):
        check_due_request_quotations()
        return ROLE_2_URL[0]
    
    elif role == os.environ.get('ROLE_3'):
        return ROLE_3_URL[0]
    
    else:
        return ROLE_4_URL[0]
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