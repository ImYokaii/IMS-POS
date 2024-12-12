import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# ===== AUTOMATIC PROCUREMENT NUMBER GENERATOR ===== #
def generate_procurement_no(DocumentType):
    
    def get_rand():
        min = int(os.environ.get('MINIMUM_INT'))
        max = int(os.environ.get('MAXIMUM_INT'))

        code = random.randint(min, max)

        return code
    
    def get_month():
        month = datetime.now()
        code = month.strftime("%m")

        return code
    
    def get_year():
        year = datetime.now()
        code = year.strftime("%Y")

        return code

    rand_code = get_rand()
    mont_code = get_month()
    year_code = get_year()
    doc_code = DocumentType
    invoice_no_arr = [doc_code, mont_code, year_code, rand_code]

    invoice_no = ''.join(map(str, invoice_no_arr))

    return invoice_no
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE PROCUREMENT NO. IF IT CATCHES AN EXISTING ONE  ===== #
def generate_unique_procurement_no(DocumentType, ModelClass):
    while True:
        procurement_no = generate_procurement_no(DocumentType)
        if not ModelClass.objects.filter(quotation_no=procurement_no).exists():
            return procurement_no
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE INVOICE NO. IF IT CATCHES AN EXISTING ONE  ===== #
def generate_unique_invoice_no(DocumentType, ModelClass):
    while True:
        procurement_no = generate_procurement_no(DocumentType)
        if not ModelClass.objects.filter(invoice_no=procurement_no).exists():
            return procurement_no
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE PROCUREMENT NO. IF IT CATCHES AN EXISTING ONE  ===== #
def create_digital_invoice(purchase_order):
    from .models import PurchaseInvoice, PurchaseInvoiceItem

    items = purchase_order.items.all()

    if not items:
        print("No items found for this purchase order.")
        return

    invoice = PurchaseInvoice.objects.create(
        purchase_order=purchase_order,
        supplier=purchase_order.supplier,
        total_amount_payable=purchase_order.total_amount,
        total_amount_payable_with_vat=purchase_order.total_amount_with_vat,
    )

    for item in items:
        PurchaseInvoiceItem.objects.create(
            purchase_invoice=invoice,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
