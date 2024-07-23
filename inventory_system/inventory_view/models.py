from django.db import models



class Product(models.Model):
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
    date_added = models.DateField(auto_now_add=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)  # (For perishable products only)
    batch_number = models.CharField(max_length=50, blank=True, null=True)  # (For perishable products only)
    brand = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Name: {self.name} (Qty. {self.quantity_in_stock})"


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
        return f"Name: {self.name} (Qty. {self.quantity})"