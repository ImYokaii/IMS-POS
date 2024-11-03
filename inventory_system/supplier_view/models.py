from django.db import models
from django.contrib.auth.models import User

class QuotationSubmission(models.Model):
    supplier = models.ForeignKey(User, on_delete=models.CASCADE)
    buyer_company_name = models.CharField(max_length=255)
    buyer_address = models.TextField()
    buyer_contact = models.CharField(max_length=255)
    quotation_no = models.CharField(max_length=50, blank=True, null=True)
    prepared_by = models.CharField(max_length=255)
    quote_valid_until = models.DateField()
    date_submitted = models.DateField(auto_now_add=True)
    terms_and_conditions = models.TextField()
    status = models.CharField(max_length=50, default="Pending")

    def __str__(self):
        return f"{self.quotation_no} - {self.buyer_company_name}"

class QuotationSubmissionItem(models.Model):
    quotation_submission = models.ForeignKey(QuotationSubmission, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} (Qty: {self.quantity})"
