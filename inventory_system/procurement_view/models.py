from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RequestQuotation(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    buyer_company_name = models.CharField(max_length=255)
    buyer_address = models.CharField(max_length=255)
    buyer_contact = models.CharField(max_length=100)
    quotation_no = models.CharField(max_length=50, unique=True) # Revise to automatically create quotation no. upon saving
    prepared_by = models.CharField(max_length=100)
    quote_valid_until = models.DateField()
    date_prepared = models.DateField(auto_now_add=True)
    terms_and_conditions = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Quotation {self.quotation_no} for {self.buyer_company_name}"

class RequestQuotationItem(models.Model):
    request_quotation = models.ForeignKey(RequestQuotation, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} - {self.quantity} units"

class QuotationSubmission(models.Model):
    supplier = models.ForeignKey(User, on_delete=models.CASCADE)
    buyer_company_name = models.CharField(max_length=255)
    buyer_address = models.TextField()
    buyer_contact = models.CharField(max_length=255)
    quotation_no = models.CharField(max_length=50)
    prepared_by = models.CharField(max_length=255)
    quote_valid_until = models.DateField()
    date_submitted = models.DateField()
    terms_and_conditions = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.quotation_no} - {self.buyer_company_name}"

class QuotationSubmissionItem(models.Model):
    quotation_submission = models.ForeignKey(QuotationSubmission, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} (Qty: {self.quantity})"