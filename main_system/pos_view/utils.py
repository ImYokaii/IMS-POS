import os
import random
from datetime import datetime
from django.db.models import Max
from dotenv import load_dotenv

load_dotenv()


# ===== AUTOMATIC PROCUREMENT NUMBER GENERATOR ===== #
def generate_invoice_no(DocumentType, ModelClass):
    max_number = ModelClass.objects.filter(invoice_no__startswith=DocumentType).aggregate(Max('invoice_no'))['invoice_no__max']

    if max_number:
        current_number = int(max_number[len(DocumentType):])
        new_number = current_number + 1
    else:
        new_number = 1

    formatted_number = f"{new_number:07d}"

    procurement_no = f"{DocumentType}{formatted_number}"

    return procurement_no
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE INVOICE NO. IF IT CATCHES AN EXISTING ONE  ===== #
def generate_unique_invoice_no(DocumentType, ModelClass):
    while True:
        invoice_no = generate_invoice_no(DocumentType, ModelClass)
        if not ModelClass.objects.filter(invoice_no=invoice_no).exists():
            return invoice_no
# =============================================== #


# ===== SEARCH FILTER PRODUCTS ===== #
def search_products(sku=None, name=None):
    from inventory_view.models import Product

    query = Product.objects.all()

    if sku:
        query = query.filter(sku=sku)

    if name:
        query = query.filter(name__icontains=name)

    return query
# =============================================== #


# ===== SEARCH FILTER INVOICES ===== #
def search_filter_invoices(invoice_no=None, transaction_date=None):
    from .models import SalesInvoice

    query = SalesInvoice.objects.all()

    if invoice_no:
        query = query.filter(invoice_no__endswith=invoice_no)

    if transaction_date:
        query = query.filter(transaction_date=transaction_date)

    return query
# =============================================== #