import os
import qrcode
import barcode
from barcode.writer import ImageWriter
import base64
from io import BytesIO
from dotenv import load_dotenv
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib import messages
from .forms import ProductForm, RestockProductForm, WasteProductForm, ProductFilterForm, WasteProductFilterForm
from .models import Product, WasteProduct
from .utils import search_filter_products, search_filter_waste_products, restock_product, transfer_to_waste
from dashboard_view.models import ProductInstance
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime


load_dotenv()


# ===== ALL PRODUCTS PAGE ===== #
@login_required(login_url=settings.LOGIN_URL)
def product_list(request):
    form = ProductFilterForm(request.GET)
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        product_type = form.cleaned_data.get('product_type')
        category = form.cleaned_data.get('category')
        status = PRODUCT_STATUS[0].strip()

        products = search_filter_products(sku, name, category, status)

    return render(request, 'product_list.html', {'form': form, 'products': products})
# =============================================== #


# ===== VIEW PRODUCT DETAILS PAGE ===== #
@login_required(login_url=settings.LOGIN_URL)
def product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Data for QR Code and Barcode
    qr_data = f"{product.sku}"
    barcode_data = f"{product.sku}"

    # Generate QR Code as Data URI
    qr = qrcode.QRCode(
        version=1,  # QR code size (1 is the smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,  # Smaller box size to make the QR code smaller
        border=1  # Smaller border size
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')
    qr_buffered = BytesIO()
    qr_img.save(qr_buffered, format="PNG")
    qr_data_uri = "data:image/png;base64," + base64.b64encode(qr_buffered.getvalue()).decode("utf-8")

    # Generate Barcode as Data URI
    barcode_cls = barcode.get_barcode_class('code128')
    barcode_instance = barcode_cls(barcode_data, writer=ImageWriter())
    barcode_writer_options = {
        'module_width': 0.2,  # Width of a single barcode line
        'module_height': 10,  # Height of the barcode
        'font_size': 8,       # Font size for text
        'text_distance': 3,   # Distance between text and barcode
        'quiet_zone': 1       # Space around the barcode
    }
    barcode_buffered = BytesIO()
    barcode_instance.write(barcode_buffered, options=barcode_writer_options)
    barcode_data_uri = "data:image/png;base64," + base64.b64encode(barcode_buffered.getvalue()).decode("utf-8")


    return render(request, 'product_view.html', 
        {'product': product,
         'qr_code': qr_data_uri,
         'barcode': barcode_data_uri})
# ============================================== #


# ===== ADDING ITEM CHOICE PAGE ===== #
@login_required(login_url=settings.LOGIN_URL)
def add_item_choice(request):
    return render(request, 'add_item_choice.html')
# =============================================== #


# ===== EXISTING PRODUCT PAGE (For Restocking) ===== #
@login_required(login_url=settings.LOGIN_URL)
def existing_product_page(request):
    form = ProductFilterForm(request.GET)
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')
        status = PRODUCT_STATUS[0].strip()

        products = search_filter_products(sku, name, category, status)

    return render(request, 'existing_product_page.html', {'form': form, 'products': products})
# =============================================== #


# ===== RESTOCKING EXISTING PRODUCT PAGE ===== #
@login_required(login_url=settings.LOGIN_URL)
def add_existing_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = RestockProductForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            try:
                restock_product(product, quantity)
                messages.success(request, f"{product.name} restocked successfully!")
                return redirect('product_list')
            
            except ValidationError as error_message:
                messages.error(request, str(error_message))
                return redirect('add_existing_product', product_id=product_id)
            
        else:
            messages.error(request, "Invalid data!")
            return redirect('add_existing_product', product_id=product_id)
            
    else:
        form = RestockProductForm()

    return render(request, 'add_existing_product.html', {'form': form, 'product': product})
# =============================================== #


# ===== ADDING PERISHABLE PRODUCT PAGE ===== #
@login_required(login_url=settings.LOGIN_URL)
def add_new_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            try:
                quantity = form.cleaned_data.get('quantity')

                if quantity is None or quantity <= 0:
                    raise ValidationError("Quantity must be greater than 0.")

                product = form.save()
                messages.success(request, "New product was added successfully!")
                return redirect('product_list')

            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('add_new_product')
        
        else:
            messages.error(request, "Invalid form input!")
            return redirect('product_list')
        
    else:
        form = ProductForm()

        return render(request, 'add_new_product.html', {'form': form})
# =============================================== #


# ===== VIEW PRODUCT WASTE PAGE ===== #
@login_required(login_url=settings.LOGIN_URL)
def wasted_product_list(request):
    form = WasteProductFilterForm(request.GET)

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')
        date_wasted = form.cleaned_data.get('date_wasted')

        products = search_filter_waste_products(sku, name, category, date_wasted)

    return render(request, 'wasted_product_list.html', {'form': form, 'products': products})
# =============================================== #


# ===== ADD PRODUCT WASTE PAGE ===== #
@login_required(login_url=settings.LOGIN_URL)
def add_product_waste(request):
    form = ProductFilterForm(request.GET)
    PRODUCT_STATUS = os.environ.get('PRODUCT_STATUS', '').split(',')

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')
        status = PRODUCT_STATUS[0].strip()

        products = search_filter_products(sku, name, category, status)

    return render(request, 'add_product_waste.html', {'form': form, 'products': products})
# =============================================== #


# ===== ADD PRODUCT TO WASTE PAGE ===== #
@login_required(login_url=settings.LOGIN_URL)
def add_to_waste(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = WasteProductForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            reason = form.cleaned_data['reason']
            employee = request.user
        
            try:
                transfer_to_waste(product, quantity, reason, employee)
                messages.success(request, f"{product.name} product transferred to waste")
                return redirect('add_product_waste')
            
            except ValidationError as error_message:
                messages.error(request, str(error_message))
                return redirect('add_existing_product', product_id=product_id)

            except ValueError as error_message:
                messages.error(request, "Invalid quantity input. Please enter a valid number.")
                return redirect('add_to_waste', product_id=product_id)
            
        else:
            messages.error(request, "Invalid data!")
            return redirect('add_to_waste', product_id=product_id)
    
    else:
        form = WasteProductForm()
    
    return render(request, 'add_to_waste.html', {'product': product})
# =============================================== #