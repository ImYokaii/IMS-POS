from django.contrib import admin
from .models import QuotationSubmission, QuotationSubmissionItem


admin.site.register(QuotationSubmission)
admin.site.register(QuotationSubmissionItem)