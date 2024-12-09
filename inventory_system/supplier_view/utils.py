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
    quotation_no_arr = [doc_code, mont_code, year_code, rand_code]

    quotation_no = ''.join(map(str, quotation_no_arr))

    return quotation_no
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE PROCUREMENT NO. IF IT CATCHES AN EXISTING ONE  ===== #
def generate_unique_procurement_no(DocumentType, ModelClass):
    while True:
        procurement_no = generate_procurement_no(DocumentType)
        if not ModelClass.objects.filter(quotation_no=procurement_no).exists():
            return procurement_no
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE PROCUREMENT NO. IF IT CATCHES AN EXISTING ONE  ===== #
def create_digital_invoice(purchase_order):
    from .models import PurchaseInvoice, PurchaseInvoiceItem

    print(f"Creating invoice for PO #{purchase_order.id}")
    items = purchase_order.items.all()
    print(f"Items in PurchaseOrder: {list(items)}")  # Debugging to verify items

    if not items:
        print("No items found for this purchase order.")
        return  # Early exit if no items are found

    invoice = PurchaseInvoice.objects.create(
        supplier=purchase_order.supplier,
        invoice_no=f"PI{purchase_order.quotation_no[2:]}",
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
