import os
from dotenv import load_dotenv
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, HttpResponse
from django.http import HttpResponseForbidden

load_dotenv()

# ===== IP LOCKING AFTER MULTIPLE FAILED ATTEMPTS ===== #
class IPLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        username = request.POST.get('username')  # Assuming username is submitted via POST

        if ip:
            key_ip = f'failed_login_attempts_{ip}'
            attempts_ip = cache.get(key_ip, 0)

            if attempts_ip >= int(os.environ.get('MAX_FAILED_LOGIN_ATTEMPTS')):
                return HttpResponseForbidden("Temporarily locked due to multiple failed login attempts. Wait for 60 seconds.")
            
            # Check user attempts
            if username:
                key_user = f'failed_login_attempts_{username}'
                attempts_user = cache.get(key_user, 0)

                if attempts_user >= int(os.environ.get('MAX_FAILED_LOGIN_ATTEMPTS')):
                    return HttpResponseForbidden("Your account has been temporarily locked due to multiple failed login attempts.")
            
        response = self.get_response(request)
        
        # Check if login attempt failed
        if request.path == settings.LOGIN_URL and request.method == "POST":

            if not request.user.is_authenticated and request.POST.get('username'):

                # Increment failed login attempts for this IP and username
                ip = self.get_client_ip(request)
                if ip:
                    key_ip = f'failed_login_attempts_{ip}'
                    attempts_ip = cache.get(key_ip, 0) + 1
                    cache.set(key_ip, attempts_ip, timeout=int(os.environ.get('FAILED_LOGIN_LOCK_DURATION')))

                username = request.POST.get('username')
                key_user = f'failed_login_attempts_{username}'
                attempts_user = cache.get(key_user, 0) + 1
                cache.set(key_user, attempts_user, timeout=int(os.environ.get('FAILED_LOGIN_LOCK_DURATION')))

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]

        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip
# =============================================== #


# ===== USER ROLE PERMISSION CONTROL ===== #
class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.LOGOUT_URL = os.environ.get('LOGOUT_URL')
        self.ROLE_1_URL = os.environ.get('ROLE_1_URL')
        self.ROLE_2_URL = os.environ.get('ROLE_2_URL').split(",")
        self.ROLE_3_URL = os.environ.get('ROLE_3_URL').split(",")
        self.ROLE_1 = os.environ.get('ROLE_1')
        self.ROLE_2 = os.environ.get('ROLE_2')
        self.ROLE_3 = os.environ.get('ROLE_3')

    def __call__(self, request):
        path = request.path

        if path == '/favicon.ico': # Prevent /favicon.co from intefering in url routing (bug)
            return HttpResponse() # It just returns a blank page
        
        print(f"User: {request.user.username}") # Check username (debugging)

        if request.user.is_authenticated:

            if path == self.LOGOUT_URL:
                return self.get_response(request)
        
            if request.user.is_superuser:
                return self.get_response(request)

            print(f"Request path: {path}") # Check requested path (debugging)

            permission = request.user.userpermission
            
            if not permission.is_permitted:
                if not (path.startswith(self.LOGOUT_URL)): # Unrestricted site for unpermitted users
                    print(f"Path: {path}") 
                    return HttpResponseForbidden("Wait for permission.")

            else:
                print(f"Role: {permission.role}")
                if permission.role == self.ROLE_1:
                    if not path.startswith(self.ROLE_1_URL):
                        print(f"Path: {path}") # Check visited path (debugging)
                        return HttpResponse("Role does not match.")

                elif permission.role == self.ROLE_2:
                    if not any(path.startswith(url.strip()) for url in self.ROLE_2_URL):
                        print(f"Path: {path}") # Check visited path (debugging)
                        return HttpResponse("Role does not match.")

                elif permission.role == self.ROLE_3:
                    if not any(path.startswith(url.strip()) for url in self.ROLE_3_URL):
                        print(f"Path: {path}") # Check visited path (debugging)
                        return HttpResponse("Role does not match.")

                else:
                    if not (path.startswith(self.LOGOUT_URL)):
                        print(f"Path: {path}") # Check visited path (debugging)
                        return HttpResponse("Wait for role permission.")
                
        response = self.get_response(request)
        return response
# =============================================== #
