import os
from dotenv import load_dotenv
from django.db import models
from django.contrib.auth.models import User

load_dotenv()

STORE_COMPANY_NAME = "AR. DJ Hardware Trading"
STORE_ADDRESS = "street bergal maligaya park, 77 Bautista, Caloocan, Metro Manila"

class UserPermission(models.Model):
    USER_ROLE_CHOICES = [
        (os.environ.get('ROLE_1'), os.environ.get('ROLE_1')),
        (os.environ.get('ROLE_2'), os.environ.get('ROLE_2')),
        (os.environ.get('ROLE_3'), os.environ.get('ROLE_3')),
        (os.environ.get('ROLE_4'), os.environ.get('ROLE_4')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    is_permitted = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='unknown')

    def __str__(self):
        return f"Username: {self.user.username} (Role: '{self.role}')"


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="suppliers")
    supplier_company_name = models.CharField(max_length=255)
    supplier_company_address = models.TextField()
    supplier_company_contact = models.CharField(max_length=20)

    def __str__(self):
        return f"Supplier: {self.user.username}, Company: {self.supplier_company_name}"