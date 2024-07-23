from django.shortcuts import render, redirect, HttpResponse
from .forms import PerishableProductForm, NonPerishableProductForm
from .models import Product


def dummy_page(request):
    return HttpResponse("Welcome to a page.")

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def add_stock_choice(request):
    return render(request, 'add_stock_choice.html')

def add_perishable(request):
    if request.method == "POST":
        form = PerishableProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_list')
        
    else:
        form = PerishableProductForm()

    return render(request, 'add_perishable.html', {'form': form})

def add_nonperishable(request):
    if request.method == "POST":
        form = NonPerishableProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_list')
        
    else:
        form = NonPerishableProductForm()

    return render(request, 'add_nonperishable.html', {'form': form})