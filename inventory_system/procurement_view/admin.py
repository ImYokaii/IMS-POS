from django.contrib import admin
from .models import RequestQuotation, RequestQuotationItem

# Register your models here.
admin.site.register(RequestQuotation)
admin.site.register(RequestQuotationItem)