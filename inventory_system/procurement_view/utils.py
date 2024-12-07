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