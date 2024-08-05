import os
from dotenv import load_dotenv
from .models import Product


load_dotenv()

# ===== FILTER PRODUCT SEARCH RESULTS ===== #
def search_filter_products(sku, name, product_type, expiration_date, category):
    products = Product.objects.all()

    if sku:
        products = products.filter(sku=sku)

    if name:
        products = products.filter(name=name)

    if product_type:
        PRODUCT_TYPES = os.environ.get('PRODUCT_TYPES', '').split(',')

        PERISHABLE_TYPE = PRODUCT_TYPES[0].strip()
        NON_PERISHABLE_TYPE = PRODUCT_TYPES[1].strip()

        if product_type == PERISHABLE_TYPE:
            products = products.filter(expiration_date__isnull=False)

        elif product_type == NON_PERISHABLE_TYPE:
            products = products.filter(expiration_date__isnull=True)

    if category:
        products = products.filter(category=category)

    if expiration_date:
        products = products.filter(expiration_date=expiration_date)

    return products
# =============================================== #