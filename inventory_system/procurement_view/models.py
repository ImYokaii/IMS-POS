from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RequestQuotation(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    buyer_company_name = models.CharField(max_length=255)
    buyer_address = models.CharField(max_length=255)
    buyer_contact = models.CharField(max_length=100)
    quotation_no = models.CharField(max_length=50, unique=True)
    prepared_by = models.CharField(max_length=100)
    quote_valid_until = models.DateField()
    date_prepared = models.DateField()
    terms_and_conditions = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Quotation {self.quotation_no} for {self.buyer_company_name}"