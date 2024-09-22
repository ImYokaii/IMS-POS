import os
from django.db import models
from dotenv import load_dotenv
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from .utils import generate_digits

load_dotenv()

class Product(models.Model):
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')
    product_status_choices = []

    for choice in PRODUCT_STATUS:
        if choice:
            product_status_choices.append((choice, choice))
    
    PRODUCT_STATUS_CHOICES = product_status_choices

    name = models.CharField(max_length=100, null=True)
    sku = models.CharField(max_length=50, unique=True, null=True)
    barcode = models.ImageField(upload_to='images/', default='barcodes/placeholder.jpg')
    category = models.CharField(max_length=50, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Selling price
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Purchase price
    supplier_name = models.CharField(max_length=100, null=True)
    date_added = models.DateField(auto_now_add=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)  # (For perishable products only)
    brand = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=PRODUCT_STATUS_CHOICES, default="Active") # Active, Expired, Wasted

    def __str__(self):
        return f"Name: {self.name} (₱ {self.selling_price}) - {self.category}"
    
    def generate_batch_number(self):
        if self.expiration_date:
            return self.expiration_date.strftime('%m%d%y')
        
        else:
            return None
        
    def generate_sku_num(self):
        category = self.category
        
        if self.expiration_date:
            type = True
        
        else:
            type = False

        self.sku = generate_digits(category, type)
        
        
    def save(self):
        if not self.sku:
            self.generate_sku_num()
        
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(f'{self.sku}',writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode.save(f'{self.name}_{'barcode.png'}', File(buffer), save=False )

        super(Product, self).save()
    