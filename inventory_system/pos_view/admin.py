from django.contrib import admin
from .models import SalesInvoice, SalesInvoiceItem, OfficialReceipt

admin.site.register(SalesInvoice)
admin.site.register(SalesInvoiceItem)
admin.site.register(OfficialReceipt)