import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from .forms import PerishableProductForm, NonPerishableProductForm, ProductFilterForm, ExistingPerishableProductForm, ExistingNonPerishableProductForm
from .models import Product
from .utils import search_filter_products, duplicate_product, transfer_to_waste
from dashboard_view.models import ProductInstance

load_dotenv()


# ===== DUMMY PAGE FOR TESTING ===== #
def dummy_page(request):
    return HttpResponse("Welcome to a page.")
# ============================================= #


# ===== ALL PRODUCTS PAGE ===== #
def product_list(request):
    form = ProductFilterForm(request.GET)
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        expiration_date = form.cleaned_data.get('expiration_date')
        category = form.cleaned_data.get('category')
        status = PRODUCT_STATUS[0].strip()

        products = search_filter_products(sku, name, product_type, expiration_date, category, status)

    return render(request, 'product_list.html', {'form': form, 'products': products})
# =============================================== #

# ===== VIEW PRODUCT DETAILS PAGE ===== #
def product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'product_view.html', {'product': product})
# =============================================== #


# ===== ADDING ITEM CHOICE PAGE ===== #
def add_item_choice(request):
    return render(request, 'add_item_choice.html')
# =============================================== #


# ===== ADDING PRODUCT TYPE PAGE ===== #
def add_product_type(request):
    return render(request, 'add_product_type.html')
# =============================================== #


# ===== EXISTING PRODUCT PAGE (For Restocking) ===== #
def existing_product_page(request):
    form = ProductFilterForm(request.GET)
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        category = form.cleaned_data.get('category')
        expiration_date = form.cleaned_data.get('expiration_date')
        status = PRODUCT_STATUS[0].strip()

        products = search_filter_products(sku, name, product_type, expiration_date, category, status)

    return render(request, 'existing_product_page.html', {'form': form, 'products': products})
# =============================================== #


# ===== RESTOCKING EXISTING PRODUCT PAGE ===== #
def add_existing_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.expiration_date:
        form_class = ExistingPerishableProductForm

    else:
        form_class = ExistingNonPerishableProductForm

    if request.method == 'POST':
        form = form_class(request.POST)

        if form.is_valid():
            if product.expiration_date:
                expiration_date = form.cleaned_data['expiration_date']
                new_product = duplicate_product(product, expiration_date)
                ProductInstance.add_or_update_instance(new_product)
                messages.success(request, f"{product.name} restocked successfully!")
            
            else:
                quantity = form.cleaned_data['quantity']

                for _ in range(quantity):
                    new_product = duplicate_product(product)
                    ProductInstance.add_or_update_instance(new_product)

                messages.success(request, f"{product.name} restocked successfully!")

            return redirect('product_list')
        
        else:
            messages.error(request, "Invalid data provided.")
        
    else:
        form = form_class()

    return render(request, 'add_existing_product.html', {'form': form, 'product': product})
# =============================================== #


# ===== ADDING PERISHABLE PRODUCT PAGE ===== #
def add_perishable(request):
    if request.method == "POST":
        form = PerishableProductForm(request.POST)

        if form.is_valid():
            product = form.save()
            ProductInstance.add_or_update_instance(product)
            messages.success(request, "New product was added successfully!")
            return redirect('product_list')
        
    else:
        messages.error(request, "Invalid Input!")
        form = PerishableProductForm()

    return render(request, 'add_perishable.html', {'form': form})
# =============================================== #


# ===== ADDING NON-PERISHABLE PRODUCT PAGE ===== #
def add_nonperishable(request):
    if request.method == "POST":
        form = NonPerishableProductForm(request.POST)

        if form.is_valid():
            product = form.save()
            ProductInstance.add_or_update_instance(product)
            messages.success(request, "New product was added successfully!")
            return redirect('product_list')
        
        else:
            for field, errors in form.errors.items():
                print(f"Field '{field}' has errors: {errors}")

    else:
        messages.error(request, "Invalid Input!")
        form = NonPerishableProductForm()

    return render(request, 'add_nonperishable.html', {'form': form})
# =============================================== #


# ===== VIEW PRODUCT WASTE PAGE ===== #
def wasted_product_list(request):
    form = ProductFilterForm(request.GET)
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        expiration_date = form.cleaned_data.get('expiration_date')
        category = form.cleaned_data.get('category')
        status = PRODUCT_STATUS[3].strip()

        products = search_filter_products(sku, name, product_type, expiration_date, category, status)

    return render(request, 'wasted_product_list.html', {'form': form, 'products': products})
# =============================================== #


# ===== ADD PRODUCT WASTE PAGE ===== #
def add_product_waste(request):
    form = ProductFilterForm(request.GET)
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        category = form.cleaned_data.get('category')
        expiration_date = form.cleaned_data.get('expiration_date')
        status = PRODUCT_STATUS[0].strip()

        products = search_filter_products(sku, name, product_type, expiration_date, category, status)

    return render(request, 'add_product_waste.html', {'form': form, 'products': products})
# =============================================== #


# ===== ADD PRODUCT TO WASTE PAGE ===== #
def add_to_waste(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        transfer_to_waste(product)
        ProductInstance.subtract_instance(product)
        messages.success(request, "Product successfully transfered to waste!")
        return redirect('wasted_product_list')
    
    return render(request, 'add_to_waste.html', {'product': product})
# =============================================== #