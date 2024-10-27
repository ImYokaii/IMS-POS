from django.contrib import admin
from .models import RequestQuotation, RequestQuotationItem, QuotationSubmission, QuotationSubmissionItem

# Register your models here.
admin.site.register(RequestQuotation)
admin.site.register(RequestQuotationItem)

admin.site.register(QuotationSubmission)
admin.site.register(QuotationSubmissionItem)