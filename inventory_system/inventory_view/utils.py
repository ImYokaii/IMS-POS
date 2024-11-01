import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ===== FILTER PRODUCT SEARCH RESULTS ===== #
def search_filter_products(sku, name, product_type, expiration_date, category, status):
    from .models import Product

    def filter(product_status):
        products = Product.objects.filter(status=product_status)
        
        if sku:
            products = products.filter(sku=sku)

        if name:
            products = products.filter(name__icontains=name)

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

    product_status = status
    results = filter(product_status)

    return results
# =============================================== #


# ===== AUTOMATIC SKU GENERATOR ===== #
def generate_digits(product_name, cost_price, category):

    def get_product(product):
        code = product[0]
        code.upper()
        return code

    def get_rounded(price):
        code = round(price)
        return code

    def get_category(c):
        if c == "Concreting and Masonry":
            code = os.environ.get('CONCRETING_AND_MASONRY')
        elif c == "Rebars and Gi Wires":
            code = os.environ.get('REBARS_AND_GI_WIRES')
        elif c == "Roofing and Insulation":
            code = os.environ.get('ROOFING_AND_INSULATION')
        elif c == "Steel":
            code = os.environ.get('STEEL')
        elif c == "Water Proofing":
            code = os.environ.get('WATER_PROOFING')
        elif c == "Sealant and Adhesive":
            code = os.environ.get('SEALANT_AND_ADHESIVE')
        elif c == "Wood Products":
            code = os.environ.get('WOOD_PRODUCTS')
        elif c == "Dry Wall and Ceiling":
            code = os.environ.get('DRY_WALL_AND_CEILING')
        elif c == "Plumbing Pipes":
            code = os.environ.get('PLUMBING_PIPES')
        elif c == "Electrical Pipes":
            code = os.environ.get('ELECTRICAL_PIPES')
        elif c == "Wires and Cables":
            code = os.environ.get('WIRES_AND_CABLES')
        elif c == "Tiling Supplies":
            code = os.environ.get('TILING_SUPPLIES')
        elif c == "Painting Supplies":
            code = os.environ.get('PAINTING_SUPPLIES')
        elif c == "Door and Cabinet Hardwares":
            code = os.environ.get('DOOR_AND_CABINET_HARDWARES')
        elif c == "Electrical Fixtures and Devices":
            code = os.environ.get('ELECTRICAL_FIXTURES_AND_DEVICES')
        elif c == "Finishing Materials":
            code = os.environ.get('FINISHING_MATERIALS')
        elif c == "Power Tools and Equipments":
            code = os.environ.get('POWER_TOOLS_AND_EQUIPMENTS')
        elif c == "Nails and Screws":
            code = os.environ.get('NAILS_AND_SCREWS')
        elif c == "Screen and Covers":
            code = os.environ.get('SCREEN_AND_COVERS')
        elif c == "Chemicals":
            code = os.environ.get('CHEMICALS')
        else:
            code = os.environ.get('UNKNOWN_CATEGORY')

        return code
    
    def get_rand():
        min = int(os.environ.get('MINIMUM_INT'))
        max = int(os.environ.get('MAXIMUM_INT'))

        code = random.randint(min, max)
        
        print(code)
        return code

    product_code = get_product(product_name)
    cost_price_code = get_rounded(cost_price)
    category_code = get_category(category)
    rand_code = get_rand()
    digit_arr = [product_code, cost_price_code, category_code, rand_code]

    digits = ''.join(map(str, digit_arr))

    return digits
# =============================================== #


# ===== GENERATE ANOTHER UNIQUE PROCUREMENT NO. IF IT CATCHES AN EXISTING ONE  ===== #
def generate_unique_sku(product_name, cost_price, category, ModelClass):
    while True:
        sku = generate_digits(product_name, cost_price, category)
        if not ModelClass.objects.filter(sku=sku).exists():
            return sku
# =============================================== #


# ===== CREATE DUPLICATE INSTANCES OF A PRODUCT BEING RESTOCKED ===== #
def duplicate_product(product, expiration_date=None):
    from .models import Product

    if product.expiration_date:
        new_product = Product(
            name=product.name,
            category=product.category,
            selling_price=product.selling_price,
            cost_price=product.cost_price,
            brand=product.brand,
            expiration_date=expiration_date,
        )

    else:
        new_product = Product(
            name=product.name,
            category=product.category,
            selling_price=product.selling_price,
            cost_price=product.cost_price,
            brand=product.brand,
            expiration_date=None,
        )

    new_product.save()
    return new_product
# =============================================== #


# ===== CREATE DUPLICATE INSTANCES OF A PRODUCT BEING RESTOCKED ===== #
def transfer_to_waste(product):
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')

    product.status = PRODUCT_STATUS[2].strip()
    product.save()
# =============================================== #