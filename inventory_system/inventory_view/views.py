from django.shortcuts import render, HttpResponse
from .models import Product


def dummy_page(request):
    return HttpResponse("Welcome to a page.")

def product_list(request):
    products = Product.objects.all()  # Retrieve all products from the database
    return render(request, 'product_list.html', {'products': products})
    