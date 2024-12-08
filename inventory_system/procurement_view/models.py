from django.db import models
from django.contrib.auth.models import User
from .utils import generate_unique_procurement_no

STORE_COMPANY_NAME = "AR. DJ Hardware Trading"
STORE_ADDRESS = "street bergal maligaya park, 77 Bautista, Caloocan, Metro Manila"

class RequestQuotation(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    buyer_company_name = models.CharField(max_length=255, default=STORE_COMPANY_NAME, null=True, blank=True)
    buyer_address = models.CharField(max_length=255, default=STORE_ADDRESS, null=True, blank=True)
    buyer_contact = models.CharField(max_length=100)
    quotation_no = models.CharField(max_length=50, unique=True)
    approved_by = models.CharField(max_length=100, null=True, blank=True)
    quote_valid_until = models.DateField(null=True, blank=True)
    date_prepared = models.DateField(auto_now_add=True)
    terms_and_conditions = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default="Ongoing", null=True, blank=True)

    def __str__(self):
        return f"Quotation {self.quotation_no} for {self.buyer_company_name}"
    
    def save(self, *args, **kwargs):
        if not self.quotation_no:
            self.quotation_no = generate_unique_procurement_no("RQ", RequestQuotation)

        super(RequestQuotation, self).save(*args, **kwargs)

class RequestQuotationItem(models.Model):
    request_quotation = models.ForeignKey(RequestQuotation, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_valid_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} - {self.quantity} units"


class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    quotation_no = models.CharField(max_length=20, unique=True)
    buyer_company_name = models.CharField(max_length=255, default=STORE_COMPANY_NAME, null=True, blank=True)
    buyer_address = models.TextField(default=STORE_ADDRESS, null=True, blank=True)
    date_ordered = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_amount_with_vat = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    approved_by = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default="Pending")

    def __str__(self):
        return f"PO #{self.quotation_no} - {self.supplier}"
    
    def save(self, *args, **kwargs):
        if not self.quotation_no:
            self.quotation_no = generate_unique_procurement_no("PO", PurchaseOrder)

        super(PurchaseOrder, self).save(*args, **kwargs)

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=25, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} (PO #{self.purchase_order.quotation_no})"