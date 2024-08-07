import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import PerishableProductForm, NonPerishableProductForm, ProductFilterForm
from .models import Product, WasteProduct
from .utils import search_filter_products
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

    initial_data = {
        'name': product.name,
        'description': product.description,
        'category': product.category,
        'price': product.price,
        'cost_price': product.cost_price,
        'unit_of_measurement': product.unit_of_measurement,
        'weight': product.weight,
        'dimensions': product.dimensions,
        'color': product.color,
        'material': product.material,
        'supplier_name': product.supplier_name,
        'brand': product.brand,
    }

    if product.expiration_date:
        initial_data['expiration_date'] = product.expiration_date
        initial_data['batch_number'] = product.batch_number
        form_class = PerishableProductForm

    else:
        form_class = NonPerishableProductForm

    if request.method == 'POST':
        form = form_class(request.POST, initial=initial_data)

        if form.is_valid():
            product = form.save()
            ProductInstance.add_or_update_instance(product)
            return redirect('product_list')
        
    else:
        form = form_class(initial=initial_data)

    return render(request, 'add_existing_product.html', {'form': form, 'product': product})
# =============================================== #


# ===== ADDING PERISHABLE PRODUCT PAGE ===== #
def add_perishable(request):
    if request.method == "POST":
        form = PerishableProductForm(request.POST)

        if form.is_valid():
            product = form.save()
            ProductInstance.add_or_update_instance(product)
            return redirect('product_list')
        
    else:
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
            return redirect('product_list')
        
    else:
        form = NonPerishableProductForm()

    return render(request, 'add_nonperishable.html', {'form': form})
# =============================================== #


# ===== ALL WASTED PRODUCTS PAGE ===== #
def wasted_product_list(request):
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        expiration_date = form.cleaned_data.get('expiration_date')
        category = form.cleaned_data.get('category')

        products = search_filter_products(sku, name, product_type, expiration_date, category)

    return render(request, 'wasted_product_list.html', {'form': form, 'products': products})
# =============================================== #


# ===== FILTER ALL PRODUCTS (FOR WASTAGE) PAGE ===== #
def filter_product_list(request):
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        category = form.cleaned_data.get('category')
        expiration_date = form.cleaned_data.get('expiration_date')

        products = search_filter_products(sku, name, product_type, expiration_date, category)

    return render(request, 'filter_product_list.html', {'form': form, 'products': products})
# =============================================== #


# ===== ADD PRODUCT TO WASTE PAGE ===== #
def add_to_waste(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        waste_product = WasteProduct(
            name=product.name,
            description=product.description,
            sku=product.sku,
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

        return redirect('filter_product_list')
    
    return render(request, 'add_to_waste.html', {'product': product})
# =============================================== #