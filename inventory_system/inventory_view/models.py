from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Selling price
    cost_price = models.DecimalField(max_digits=10, decimal_places=2) # Purchase price
    quantity_in_stock = models.PositiveIntegerField() 
    unit_of_measurement = models.CharField(max_length=50)  # (e.g kg, liters, pieces)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) 
    dimensions = models.CharField(max_length=100, blank=True) # Length x Height x Weight 
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=50, blank=True)
    supplier_name = models.CharField(max_length=100)
    supplier_contact = models.CharField(max_length=100, blank=True)
    reorder_level = models.PositiveIntegerField() # Measured against quantity in stock
    last_restock_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)  # (For perishable products only)
    batch_number = models.CharField(max_length=50, blank=True)  # (For perishable products only)
    warranty_period = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Name: {self.name} (Qty. {self.quantity_in_stock})"

