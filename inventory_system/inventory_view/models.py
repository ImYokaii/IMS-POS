from django.db import models
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from .utils import generate_digits

class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, null=True)
    barcode = models.ImageField(upload_to='images/', default='barcodes/placeholder.jpg')
    category = models.CharField(max_length=50, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Selling price
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Purchase price
    unit_of_measurement = models.CharField(max_length=50, blank=True, null=True)  # (e.g kg, liters, pieces)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)  # Length x Height x Weight
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=50, blank=True, null=True)
    supplier_name = models.CharField(max_length=100, null=True)
    date_added = models.DateField(auto_now_add=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)  # (For perishable products only)
    batch_number = models.CharField(max_length=50, blank=True, null=True)  # (For perishable products only)
    brand = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Name: {self.name} (₱ {self.price})"
    
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
        print(self.sku)
        
    def save(self):
        if self.expiration_date and not self.batch_number:
            self.batch_number = self.generate_batch_number()

        self.generate_sku_num()

        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(f'{self.sku}',writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode.save(f'{self.name}_{'barcode.png'}', File(buffer), save=False )

        super(Product, self).save()

class WasteProduct(models.Model):
    name = models.CharField(max_length=100, null=True)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, null=True)
    category = models.CharField(max_length=50, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Selling price
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Purchase price
    unit_of_measurement = models.CharField(max_length=50, blank=True, null=True)  # (e.g kg, liters, pieces)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)  # Length x Height x Weight
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=50, blank=True, null=True)
    supplier_name = models.CharField(max_length=100, null=True)
    date_added = models.DateField(auto_now_add=True)
    expiration_date = models.DateField(blank=True, null=True)  # (For perishable products only)
    batch_number = models.CharField(max_length=50, blank=True, null=True)  # (For perishable products only)
    brand = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"Name: {self.name} (Date of Waste: {self.date_added})"
    
