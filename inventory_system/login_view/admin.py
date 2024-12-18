from django.contrib import admin
from .models import UserPermission, Supplier


admin.site.register(UserPermission)
admin.site.register(Supplier)