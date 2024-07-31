from django.shortcuts import render, HttpResponse
from inventory_view.models import Product
from .models import ProductInstance


# ===== Dashboard Page ===== #
def dashboard(request):
    total_products = Product.objects.all().count()

    return render(request, 'dashboard.html', {'total_products': total_products})
# =============================================== #


# ===== Dashboard Page ===== #
def product_levels(request):
    product_instance = ProductInstance.objects.all()

    return render(request, 'product_levels.html', {'product_instance': product_instance})
# =============================================== #