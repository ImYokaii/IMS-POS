import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# ===== AUTOMATIC PROCUREMENT NUMBER GENERATOR ===== #
def generate_invoice_no(DocumentType):
    
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


# ===== GENERATE ANOTHER UNIQUE INVOICE NO. IF IT CATCHES AN EXISTING ONE  ===== #
def generate_unique_invoice_no(DocumentType, ModelClass):
    while True:
        invoice_no = generate_invoice_no(DocumentType)
        if not ModelClass.objects.filter(invoice_no=invoice_no).exists():
            return invoice_no
# =============================================== #


# ===== SEARCH FILTER  ===== #
def search_products(sku=None, name=None):
    from inventory_view.models import Product

    query = Product.objects.all()

    if sku:
        query = query.filter(sku=sku)

    if name:
        query = query.filter(name__icontains=name)

    print(f"Prodcut searched: {query}")
    return query
# =============================================== #