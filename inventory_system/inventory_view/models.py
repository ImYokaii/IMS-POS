import os
from django.db import models
from dotenv import load_dotenv
from django.core.files import File
from django.contrib.auth.models import User
# from .utils import generate_digits

load_dotenv()

class Product(models.Model):
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')
    product_status_choices = []

    for choice in PRODUCT_STATUS:
        if choice:
            product_status_choices.append((choice, choice))
    PRODUCT_STATUS_CHOICES = product_status_choices

    name = models.CharField(max_length=100, null=True)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    category = models.CharField(max_length=50, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Selling price
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Purchase price
    date_added = models.DateField(auto_now_add=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)  # (For perishable products only)
    brand = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=PRODUCT_STATUS_CHOICES, default="Active") # Active, Expired, Wasted

    def __str__(self):
        return f"Name: {self.name} (₱ {self.selling_price}) - {self.category}"
        
    # def generate_sku_num(self):
    #     category = self.category
        
    #     if self.expiration_date:
    #         type = True
        
    #     else:
    #         type = False

    #     self.sku = generate_unique_sku(category, type)
        
        
    def save(self):
        # if not self.sku:
        #     self.generate_sku_num()

        super(Product, self).save()
    