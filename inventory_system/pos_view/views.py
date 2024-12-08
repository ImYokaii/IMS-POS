from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from inventory_view.models import Product
from .models import SalesInvoice, SalesInvoiceItem
from .utils import search_products
from decimal import Decimal
from dotenv import load_dotenv
import os

load_dotenv()

def pos_page(request):
    invoice = SalesInvoice.objects.filter(status='Pending').first()
    
    if not invoice:
        invoice = SalesInvoice.objects.create(employee_id=request.user, total_amount=0, cash_tendered=0, status='Pending')

    items = SalesInvoiceItem.objects.filter(invoice=invoice)
    total_amount = sum(item.unit_price * item.quantity for item in items)
    vat = total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    total_with_vat = total_amount + vat

    invoice.total_amount_with_vat = total_with_vat
    invoice.save()

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
        'vat': vat,
        'total_with_vat': total_with_vat,
        'products': products,
        'search_sku': search_sku,
        'search_name': search_name,
        'item_totals': item_totals,
        'has_items': has_items,
    })


def add_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = get_object_or_404(Product, id=product_id)

        if product.selling_price <= 0:
            messages.error(request, "This product cannot be added to the invoice because its selling price is 0.")
            return redirect('pos_page')
        
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

    # Handle GET request for SKU submission
    sku = request.GET.get('sku')
    if sku:
        product = get_object_or_404(Product, sku=sku)
        return render(request, 'add_item_form.html', {'product': product})

    return redirect('pos_page')


def complete_invoice(request):
    invoice = SalesInvoice.objects.filter(status='Pending').first()
    items = SalesInvoiceItem.objects.filter(invoice=invoice)

    total_amount = sum(item.unit_price * item.quantity for item in items)
    vat = total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    total_with_vat = total_amount + vat

    invoice.total_amount = total_amount
    invoice.total_amount_with_vat = total_with_vat
    invoice.save()

    return redirect('input_cash', invoice.id)


def input_cash(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)

    if request.method == 'POST':
        cash_tendered = Decimal(request.POST.get('cash_tendered', 0))
        
        if cash_tendered >= invoice.total_amount_with_vat:
            invoice.cash_tendered = cash_tendered
            invoice.save()

            return redirect('transaction_summary', invoice.id)
        
        else:
            messages.error(request, "Cash tendered is less than the total amount payable.")
            return redirect('input_cash', invoice.id)

    return render(request, 'input_cash.html', {
        'invoice': invoice,
        'total_amount_with_vat': invoice.total_amount_with_vat,
    })


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


def transaction_summary(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)

    change = invoice.cash_tendered - invoice.total_amount_with_vat

    return render(request, 'transaction_summary.html', {
        'invoice': invoice,
        'change': change,
    })


def finish_transaction(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)

    invoice.status = 'Paid'
    invoice.save()

    items = SalesInvoiceItem.objects.filter(invoice=invoice)
    for item in items:
        product = Product.objects.filter(name=item.product_name).first()
        if product:
            if item.quantity > product.quantity:
                messages.error(request, f"Not enough stock for {product.name}. Available Stock: {product.quantity}, Requested: {item.quantity}")
                return redirect('pos_page')
            product.quantity -= item.quantity
            product.save()

    messages.success(request, "Transaction finished successfully.")
    return redirect('pos_page')

def completed_transactions(request):
    # Filter the invoices that are completed (status = 'Paid')
    completed_invoices = SalesInvoice.objects.filter(status='Paid').order_by('-transaction_date')

    # Prepare to display the relevant data
    return render(request, 'completed_transactions.html', {
        'completed_invoices': completed_invoices,
    })