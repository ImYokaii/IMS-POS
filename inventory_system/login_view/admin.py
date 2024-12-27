from django.contrib import admin
from .models import UserPermission, CompanyProfile


admin.site.register(UserPermission)
admin.site.register(CompanyProfile)