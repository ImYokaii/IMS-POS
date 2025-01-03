import os
import random
from datetime import datetime
from django.db.models import Max
from dotenv import load_dotenv


load_dotenv()


# ===== AUTOMATIC INCREMENTAL PROCUREMENT NUMBER GENERATOR ===== #
def generate_procurement_no(DocumentType, ModelClass):
    max_number = ModelClass.objects.filter(quotation_no__startswith=DocumentType).aggregate(Max('quotation_no'))['quotation_no__max']

    if max_number:
        current_number = int(max_number[len(DocumentType):])
        new_number = current_number + 1
    else:
        new_number = 1

    formatted_number = f"{new_number:07d}"

    procurement_no = f"{DocumentType}{formatted_number}"

    return procurement_no
# =============================================== #


# ===== GENERATE UNIQUE PROCUREMENT NO. FOR A MODEL ===== #
def generate_unique_procurement_no(DocumentType, ModelClass):
    while True:
        procurement_no = generate_procurement_no(DocumentType, ModelClass)
        if not ModelClass.objects.filter(quotation_no=procurement_no).exists():
            return procurement_no
# =============================================== #


# ===== RESTOCK OR ADD NEW PRODUCT (PROCUREMENT) ===== #
def add_or_update_product(product_name, quantity, cost_price):
    from inventory_view.models import Product

    print(f"Attempting to add or update product: {product_name}")
    product = Product.objects.filter(name=product_name).first()

    if product:
        print(f"Product found: {product_name}. Current quantity: {product.quantity}. Adding: {quantity}.")
        product.quantity += quantity
        product.save()

    else:
        print(f"Product not found: {product_name}. Creating new product.")
        Product.objects.create(
            name=product_name,
            quantity=quantity,
            cost_price=cost_price,
        )
# =============================================== #


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