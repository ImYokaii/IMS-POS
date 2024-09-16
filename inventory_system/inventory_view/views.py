import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from .forms import PerishableProductForm, NonPerishableProductForm, ProductFilterForm, ExistingPerishableProductForm, ExistingNonPerishableProductForm
from .models import Product, WasteProduct
from .utils import search_filter_products, search_filter_wasted_products, duplicate_product
from dashboard_view.models import ProductInstance

load_dotenv()


# ===== DUMMY PAGE FOR TESTING ===== #
def dummy_page(request):
    return HttpResponse("Welcome to a page.")
# =============================================== #


# ===== ALL PRODUCTS PAGE ===== #
def product_list(request):
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        expiration_date = form.cleaned_data.get('expiration_date')
        category = form.cleaned_data.get('category')

        products = search_filter_products(sku, name, product_type, expiration_date, category)

    return render(request, 'product_list.html', {'form': form, 'products': products})
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

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        category = form.cleaned_data.get('category')
        expiration_date = form.cleaned_data.get('expiration_date')

        products = search_filter_products(sku, name, product_type, expiration_date, category)

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
        messages.error(request, "Invalid Input!")
        form = NonPerishableProductForm()

    return render(request, 'add_nonperishable.html', {'form': form})
# =============================================== #


# ===== VIEW PRODUCT WASTE PAGE ===== #
def wasted_product_list(request):
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        expiration_date = form.cleaned_data.get('expiration_date')
        category = form.cleaned_data.get('category')

        products = search_filter_wasted_products(sku, name, product_type, expiration_date, category)

    return render(request, 'wasted_product_list.html', {'form': form, 'products': products})
# =============================================== #


# ===== ADD PRODUCT WASTE PAGE ===== #
def add_product_waste(request):
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        category = form.cleaned_data.get('category')
        expiration_date = form.cleaned_data.get('expiration_date')

        products = search_filter_products(sku, name, product_type, expiration_date, category)

    return render(request, 'add_product_waste.html', {'form': form, 'products': products})
# =============================================== #


# ===== ADD PRODUCT TO WASTE PAGE ===== #
def add_to_waste(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        waste_product = WasteProduct(
            name=product.name,
            description=product.description,
            category=product.category,
            price=product.price,
            cost_price=product.cost_price,
            unit_of_measurement=product.unit_of_measurement,
            weight=product.weight,
            dimensions=product.dimensions,
            color=product.color,
            material=product.material,
            supplier_name=product.supplier_name,
            expiration_date=product.expiration_date,
            batch_number=product.batch_number,
            brand=product.brand,
        )

        waste_product.save()
        product.delete()
        
        messages.success(request, "Product successfully transfered to waste!")

        return redirect('wasted_product_list')
    
    return render(request, 'add_to_waste.html', {'product': product})
# =============================================== #