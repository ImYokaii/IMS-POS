from django.db import models
from django.contrib.auth.models import User
from .utils import generate_unique_procurement_no

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


class PurchaseInvoice(models.Model):
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    invoice_no = models.CharField(max_length=50, unique=True, blank=True, null=True)
    supplier_company_name = models.CharField(max_length=255, blank=True, null=True)
    supplier_address = models.TextField(blank=True, null=True)
    date_issued = models.DateField(auto_now_add=True, blank=True, null=True)
    total_amount_payable = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default="Pending")

    def __str__(self):
        return f"PI #{self.invoice_no} - {self.supplier_company_name}"

class PurchaseInvoiceItem(models.Model):
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} - {self.quantity} units"