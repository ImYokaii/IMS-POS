import os
from django.db import models
from dotenv import load_dotenv
from django.core.files import File
from django.contrib.auth.models import User
from .utils import generate_unique_sku


load_dotenv()

class Product(models.Model):
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')
    product_status_choices = []

    for choice in PRODUCT_STATUS:
        if choice:
            product_status_choices.append((choice, choice))
    PRODUCT_STATUS_CHOICES = product_status_choices

    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=50, null=True)
    quantity = models.IntegerField(null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Selling price
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Purchase price
    status = models.CharField(max_length=50, choices=PRODUCT_STATUS_CHOICES, default="Active") # Active, Inactive

    def __str__(self):
        return f"Name: {self.name} (₱ {self.selling_price}) - {self.category}"
        
    def generate_sku_num(self):
        self.sku = generate_unique_sku(self.name, self.cost_price, self.category, Product)
        
        
    def save(self):
        if not self.sku:
            self.generate_sku_num()

        super(Product, self).save()


class WasteProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="waste_records")
    quantity = models.PositiveIntegerField()
    reason = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_wasted = models.DateField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.quantity} units of {self.product.name} transferred to waste"