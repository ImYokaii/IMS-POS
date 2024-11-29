from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from inventory_view.models import Product
from .models import SalesInvoice, SalesInvoiceItem
from .forms import ProductSearchForm
from .utils import search_products


def pos_page(request):
    invoice = SalesInvoice.objects.filter(status='Pending', employee_id=request.user).first()
    if not invoice:
        invoice = SalesInvoice.objects.create(employee_id=request.user, total_amount=0, cash_tendered=0, status='Pending')

    items = SalesInvoiceItem.objects.filter(invoice=invoice)
    total_amount = sum(item.unit_price * item.quantity for item in items)

    search_sku = request.GET.get('sku')
    search_name = request.GET.get('name')
    products = None

    if search_sku or search_name:
        products = search_products(sku=search_sku, name=search_name)

    item_totals = [(item, item.unit_price * item.quantity) for item in items]

    has_items = items.exists()

    return render(request, 'pos_page.html', {
        'invoice': invoice,
        'items': items,
        'total_amount': total_amount,
        'products': products,
        'search_sku': search_sku,
        'search_name': search_name,
        'item_totals': item_totals,
        'has_items': has_items
    })


def add_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = get_object_or_404(Product, id=product_id)
        invoice = SalesInvoice.objects.filter(status='Pending', employee_id=request.user).first()

        if not invoice:
            invoice = SalesInvoice.objects.create(employee_id=request.user, total_amount=0, cash_tendered=0, status='Pending')

        existing_item = SalesInvoiceItem.objects.filter(invoice=invoice, product_name=product.name).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()

        else:
            SalesInvoiceItem.objects.create(invoice=invoice, product_name=product.name, quantity=quantity, unit_price=product.selling_price)

    return redirect('pos_page')


def complete_invoice(request):
    invoice = SalesInvoice.objects.filter(status='Pending').first()
    items = SalesInvoiceItem.objects.filter(invoice=invoice)

    for item in items:
        product = Product.objects.filter(name=item.product_name).first()
        if product and item.quantity > product.quantity:
            messages.error(request, f"Not enough stock for {product.name}. Available Stock: {product.quantity}, Requested: {item.quantity}")
            return redirect('pos_page')
    
    for item in items:
        product = Product.objects.filter(name=item.product_name).first()
        if product:
            product.quantity -= item.quantity
            product.save()

    items = SalesInvoiceItem.objects.filter(invoice=invoice)
    total_amount = sum(item.unit_price * item.quantity for item in items)
    invoice.total_amount = total_amount
    invoice.status = 'Completed'
    invoice.save()

    return render(request, 'pos_page')

    return render(request, 'pos_page.html', 
        {'message': 'Invoice successfully completed',
         'invoice': invoice,
         'total_amount': total_amount})


def edit_item(request, item_id):
    item = get_object_or_404(SalesInvoiceItem, id=item_id)
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', item.quantity))
        item.quantity = new_quantity
        item.save()
    return redirect('pos_page')


def delete_item(request, item_id):
    item = get_object_or_404(SalesInvoiceItem, id=item_id)
    item.delete()
    return redirect('pos_page')
