from django.db import models
from inventory_view.models import Product
from django.contrib.auth.models import User
from .utils import generate_unique_invoice_no


STORE_COMPANY_NAME = "AR. DJ Hardware Trading"
STORE_ADDRESS = "street bergal maligaya park, 77 Bautista, Caloocan, Metro Manila"
CONTACT_NO = "09123456789"

class SalesInvoice(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Voided', 'Voided'),
    ]
    
    invoice_no = models.CharField(max_length=50, unique=True)
    transaction_date = models.DateField(auto_now_add=True)
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='sales_invoices')
    company_name = models.CharField(max_length=255, default=STORE_COMPANY_NAME, null=True, blank=True)
    company_address = models.TextField(default=STORE_ADDRESS, null=True, blank=True)
    contact_no = models.CharField(max_length=15, default=CONTACT_NO, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_amount_with_vat = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    cash_tendered = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Invoice No: {self.invoice_no} - {self.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = generate_unique_invoice_no("SI", SalesInvoice)

        super(SalesInvoice, self).save(*args, **kwargs)

class SalesInvoiceItem(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='invoice_items')
    product_name = models.CharField(max_length=255,null=True, blank=True)
    quantity = models.PositiveIntegerField()
    measurement = models.CharField(max_length=50, null=True, blank=True, default="No Measurement")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item for Invoice No: {self.invoice.invoice_no}"


class OfficialReceipt(models.Model):
    sales_invoice = models.ForeignKey('SalesInvoice', on_delete=models.CASCADE, related_name='official_receipt')
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='issued_receipts')
    invoice_no = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=255, default=STORE_COMPANY_NAME, null=True, blank=True)
    company_address = models.TextField(default=STORE_ADDRESS, null=True, blank=True)
    receipt_date = models.DateField(auto_now_add=True)
    vat = models.DecimalField(max_digits=20, decimal_places=2)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    total_amount_with_vat = models.DecimalField(max_digits=20, decimal_places=2)
    
    
    def __str__(self):
        return f"Receipt No: {self.invoice_no} for Invoice No: {self.sales_invoice.invoice_no}"

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.invoice_no = generate_unique_invoice_no("OR", OfficialReceipt)
        super(OfficialReceipt, self).save(*args, **kwargs)