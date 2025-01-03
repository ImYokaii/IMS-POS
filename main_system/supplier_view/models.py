from django.db import models
from django.contrib.auth.models import User
from procurement_view.models import RequestQuotation, PurchaseOrder
from .utils import generate_unique_procurement_no, generate_unique_invoice_no

STORE_COMPANY_NAME = "AR. DJ Hardware Trading"
STORE_ADDRESS = "street bergal maligaya park, 77 Bautista, Caloocan, Metro Manila"

class QuotationSubmission(models.Model):
    from procurement_view.models import RequestQuotation
    
    request_quotation = models.ForeignKey(RequestQuotation, on_delete=models.CASCADE, related_name="quotation_submissions", null=True, blank=True)
    supplier = models.ForeignKey(User, on_delete=models.CASCADE)
    buyer_company_name = models.CharField(max_length=255, default=STORE_COMPANY_NAME)
    buyer_address = models.TextField(default=STORE_ADDRESS)
    buyer_contact = models.CharField(max_length=255)
    supplier_company_name = models.CharField(max_length=255, null=True, blank= True)
    supplier_company_address = models.CharField(max_length=255, null=True, blank= True)
    supplier_company_contact = models.CharField(max_length=255, null=True, blank=True)
    quotation_no = models.CharField(max_length=50, blank=True, null=True)
    prepared_by = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    total_amount_with_vat = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    quote_valid_until = models.DateField()
    date_submitted = models.DateField(auto_now_add=True)
    terms_and_conditions = models.TextField()
    status = models.CharField(max_length=50, default="Pending")

    def __str__(self):
        return f"{self.quotation_no} - {self.buyer_company_name}"
    
    def save(self, *args, **kwargs):
        if not self.quotation_no:
            self.quotation_no = generate_unique_procurement_no("QS", QuotationSubmission)

        super(QuotationSubmission, self).save(*args, **kwargs)

class QuotationSubmissionItem(models.Model):
    quotation_submission = models.ForeignKey(QuotationSubmission, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField(null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    measurement = models.CharField(max_length=50, null=True)
    price_valid_until = models.DateField(null=True)

    def __str__(self):
        return f"{self.product_name} (Qty: {self.quantity})"


class PurchaseInvoice(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='purchase_invoices', null=True)
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    invoice_no = models.CharField(max_length=50, unique=True, blank=True, null=True)
    buyer_company_name = models.CharField(max_length=255, default=STORE_COMPANY_NAME)
    buyer_address = models.TextField(default=STORE_ADDRESS)
    supplier_company_name = models.CharField(max_length=255, null=True, blank= True)
    supplier_company_address = models.CharField(max_length=255, null=True, blank= True)
    supplier_company_contact = models.CharField(max_length=255, null=True, blank=True)
    date_issued = models.DateField(auto_now_add=True, blank=True, null=True)
    total_amount_payable = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    total_amount_payable_with_vat = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default="Pending")

    def __str__(self):
        return f"PI #{self.invoice_no} - {self.supplier_company_name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = generate_unique_invoice_no("PI", PurchaseInvoice)

        super(PurchaseInvoice, self).save(*args, **kwargs)

class PurchaseInvoiceItem(models.Model):
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    measurement = models.CharField(max_length=50, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} - {self.quantity} units"