import os
from dotenv import load_dotenv
from django.db import models
from django.contrib.auth.models import User

load_dotenv()

class UserPermission(models.Model):
    USER_ROLE_CHOICES = [
        (os.environ.get('ROLE_1'), 'Manager'),
        (os.environ.get('ROLE_2'), 'Employee'),
        (os.environ.get('ROLE_3'), 'Supplier'),
        (os.environ.get('ROLE_4'), 'Unkown'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    is_permitted = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='unknown')

    def __str__(self):
        return f"Username: {self.user.username} (Role: '{self.role}')"