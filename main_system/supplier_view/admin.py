from django.contrib import admin
from .models import QuotationSubmission, QuotationSubmissionItem, PurchaseInvoice, PurchaseInvoiceItem


admin.site.register(QuotationSubmission)
admin.site.register(QuotationSubmissionItem)

admin.site.register(PurchaseInvoice)
admin.site.register(PurchaseInvoiceItem)