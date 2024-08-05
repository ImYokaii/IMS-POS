from .models import ProductInstance


# ===== FILTER PRODUCT LIST RESULT ===== #
def search_filter_product_list(name, category):
    product_instance = ProductInstance.objects.all()

    if name:
        product_instance = product_instance.filter(name=name)

    if category:
        product_instance = product_instance.filter(category=category)

    return product_instance
# =============================================== #