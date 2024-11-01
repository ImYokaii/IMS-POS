from django.contrib import admin
from .models import RequestQuotation, RequestQuotationItem, PurchaseOrder, PurchaseOrderItem

# Register your models here.
admin.site.register(RequestQuotation)
admin.site.register(RequestQuotationItem)

admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)