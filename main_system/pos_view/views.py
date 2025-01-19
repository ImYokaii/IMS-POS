from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from inventory_view.models import Product
from .models import SalesInvoice, SalesInvoiceItem, OfficialReceipt
from .utils import search_products, search_filter_invoices
from .forms import InvoiceSearchForm
from decimal import Decimal
from dotenv import load_dotenv
import os
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.paginator import Paginator


load_dotenv()

@login_required(login_url="/login/")
def pos_page(request):
    invoice = SalesInvoice.objects.filter().order_by('-id').first()
    
    if invoice is None or invoice.status in ["Paid", "Voided", "Refunded"]:
        invoice = SalesInvoice.objects.create(employee_id=None, total_amount=0, cash_tendered=0, status='Pending')

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


@login_required(login_url="/login/")
def add_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = get_object_or_404(Product, id=product_id)

        if product.selling_price <= 0:
            messages.error(request, "This product cannot be added to the invoice because its selling price is 0.")
            return redirect('pos_page')

        if product.quantity < quantity:
            messages.error(request, "Error! Quantity can not be greater than the inventory quantity.")
            return redirect('pos_page')
        
        invoice = SalesInvoice.objects.filter().order_by('-id').first()

        existing_item = SalesInvoiceItem.objects.filter(invoice=invoice, product_name=product.name).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()

        else:
            SalesInvoiceItem.objects.create(invoice=invoice, product_name=product.name, quantity=quantity, measurement=product.measurement, unit_price=product.selling_price)

        return redirect('pos_page')

    sku = request.GET.get('sku')
    if sku:
        product = get_object_or_404(Product, sku=sku)
        return render(request, 'add_item_form.html', {'product': product})

    return redirect('pos_page')


@login_required(login_url="/login/")
def complete_invoice(request):
    invoice = SalesInvoice.objects.filter().order_by('-id').first()

    if invoice.status == "Paid":
        messages.error(request, "Error! That transaction is already paid.")
        return redirect('pos_page')
    
    items = SalesInvoiceItem.objects.filter(invoice=invoice)

    total_amount = sum(item.unit_price * item.quantity for item in items)
    vat = total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    total_with_vat = total_amount + vat

    invoice.employee_id = request.user
    invoice.total_amount = total_amount
    invoice.total_amount_with_vat = total_with_vat
    invoice.status = "Completed"
    invoice.save()

    return redirect('input_cash', invoice.id)


@login_required(login_url="/login/")
def input_cash(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)

    if invoice.status == "Paid":
        messages.error(request, "Error! That transaction is already paid.")
        return redirect('pos_page')

    else:
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


@login_required(login_url="/login/")
def edit_item(request, item_id):
    item = get_object_or_404(SalesInvoiceItem, id=item_id)
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', item.quantity))
        item.quantity = new_quantity
        item.save()
    return redirect('pos_page')


@login_required(login_url="/login/")
def delete_item(request, item_id):
    item = get_object_or_404(SalesInvoiceItem, id=item_id)
    item.delete()
    return redirect('pos_page')


@login_required(login_url="/login/")
def transaction_summary(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)

    if invoice.status == 'Paid':
        messages.error(request, "Error! That transaction is already paid.")
        return redirect('pos_page')

    change = invoice.cash_tendered - invoice.total_amount_with_vat

    return render(request, 'transaction_summary.html', {
        'invoice': invoice,
        'change': change,
    })


@login_required(login_url="/login/")
def finish_transaction(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)

    if invoice.status == 'Paid':
        messages.error(request, "Error! That transaction is already paid.")
        return redirect('pos_page')

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

    vat = invoice.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    OfficialReceipt.objects.create(
        sales_invoice=invoice,
        issued_by=request.user,
        vat=vat,
        total_amount=invoice.total_amount,
        total_amount_with_vat=invoice.total_amount_with_vat,
    )

    return redirect('receipt_page', invoice.id)


@login_required(login_url="/login/")
def receipt_page(request, invoice_id):
    is_two = OfficialReceipt.objects.filter(sales_invoice__id=invoice_id).count()

    if is_two >= 2:
        messages.error(request, "Error! That transaction is already paid.")
        return redirect('pos_page')

    official_receipt = get_object_or_404(OfficialReceipt, sales_invoice__id=invoice_id)

    return render(request, 'receipt_page.html', {
        'official_receipt': official_receipt,
    })


@login_required(login_url="/login/")
def transaction_invoices(request):
    form = InvoiceSearchForm(request.GET)

    if form.is_valid():
        invoice_no = form.cleaned_data.get('invoice_no')
        transaction_date = form.cleaned_data.get('receipt_date')

        transaction_invoices = search_filter_invoices(invoice_no, transaction_date)

        transaction_invoices = (
            search_filter_invoices(invoice_no, transaction_date)
            .order_by('-invoice_no')
        )

    paginator = Paginator(transaction_invoices, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'transaction_invoices.html', {
        'page_obj': page_obj,
    })


@login_required(login_url="/login/")
def transaction_invoices_detail(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)
    items = SalesInvoiceItem.objects.filter(invoice=invoice)
    
    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = invoice.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    change = invoice.cash_tendered - invoice.total_amount_with_vat

    if request.method == "POST":
        if 'voided' in request.POST:
            invoice.status = "Voided"
            invoice.total_amount = 0
            invoice.total_amount_with_vat = 0
            invoice.save()

        elif 'refunded' in request.POST:
            invoice.status = "Refunded"
            invoice.total_amount = 0
            invoice.total_amount_with_vat = 0
            invoice.cash_tendered = 0
            invoice.save()

    return render(request, 'transaction_invoices_detail.html', {
        'invoice': invoice,
        'items': items,
        'vat': vat,
        'change': change,
    })


@login_required(login_url="/login/")
def download_sales_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice, id=invoice_id)
    items = SalesInvoiceItem.objects.filter(invoice=invoice)

    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = invoice.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))

    context = {
        'invoice': invoice,
        'items': items,
        'vat': vat,
    }

    template = get_template('download_sales_invoice_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales-invoice_{invoice.invoice_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response