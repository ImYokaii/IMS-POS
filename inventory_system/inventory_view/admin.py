from django.contrib import admin
from .models import Product, WasteProduct


admin.site.register(Product)
admin.site.register(WasteProduct)