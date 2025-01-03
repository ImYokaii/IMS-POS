import os
import random
from datetime import datetime
from django.db.models import Max
from dotenv import load_dotenv

load_dotenv()


# ===== AUTOMATIC PROCUREMENT NUMBER GENERATOR ===== #
def generate_procurement_no(DocumentType, ModelClass):

    if DocumentType == "QS":
        max_number = ModelClass.objects.filter(quotation_no__startswith=DocumentType).aggregate(Max('quotation_no'))['quotation_no__max']
    
    if DocumentType == "PI":
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


# ===== GENERATE ANOTHER UNIQUE PROCUREMENT NO. IF IT CATCHES AN EXISTING ONE  ===== #
def generate_unique_procurement_no(DocumentType, ModelClass):
    while True:
        procurement_no = generate_procurement_no(DocumentType, ModelClass)
        if not ModelClass.objects.filter(quotation_no=procurement_no).exists():
            return procurement_no
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE INVOICE NO. IF IT CATCHES AN EXISTING ONE  ===== #
def generate_unique_invoice_no(DocumentType, ModelClass):
    while True:
        procurement_no = generate_procurement_no(DocumentType, ModelClass)
        if not ModelClass.objects.filter(invoice_no=procurement_no).exists():
            return procurement_no
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE PROCUREMENT NO. IF IT CATCHES AN EXISTING ONE  ===== #
def create_digital_invoice(purchase_order):
    from .models import PurchaseInvoice, PurchaseInvoiceItem
    from login_view.models import CompanyProfile

    items = purchase_order.items.all()

    supplier = CompanyProfile.objects.get(user=purchase_order.supplier)

    if not items:
        print("No items found for this purchase order.")
        return

    invoice = PurchaseInvoice.objects.create(
        purchase_order=purchase_order,
        supplier=purchase_order.supplier,
        supplier_company_name=supplier.company_name,
        supplier_company_address=supplier.company_address,
        supplier_company_contact=supplier.company_contact,
        total_amount_payable=purchase_order.total_amount,
        total_amount_payable_with_vat=purchase_order.total_amount_with_vat,
    )

    for item in items:
        PurchaseInvoiceItem.objects.create(
            purchase_invoice=invoice,
            product_name=item.product_name,
            measurement=item.measurement,
            quantity=item.quantity,
            unit_price=item.unit_price
        )


# ===== URL SIGNER ===== #
from django.core.signing import Signer, BadSignature
signer = Signer()

def sign_id(id):
    return signer.sign(id)

def unsign_id(signed_id):
    try:
        return signer.unsign(signed_id)
    except BadSignature:
        return None
# =============================================== #
