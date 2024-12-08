import os
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequestQuotationForm, RequestQuotationItemForm, RequestQuotationItemFormSet, PurchaseOrderForm, PurchaseOrderItemFormSet, PurchaseInvoiceForm
from .models import RequestQuotation, RequestQuotationItem, PurchaseOrder, PurchaseOrderItem
from .utils import add_or_update_product
from supplier_view.models import QuotationSubmission, QuotationSubmissionItem, PurchaseInvoice, PurchaseInvoiceItem
from django.http import HttpResponse
from django.utils import timezone
from datetime import date
from decimal import Decimal
from dotenv import load_dotenv
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages


load_dotenv()


@login_required(login_url=settings.LOGIN_URL)
def create_request_quotation(request):
    if request.method == "POST":
        form = RequestQuotationForm(request.POST)
        formset = RequestQuotationItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            request_quotation = form.save(commit=False)
            request_quotation.employee = request.user
            request_quotation = form.save()

            for form in formset:
                if form.cleaned_data:
                    request_quotation_item = form.save(commit=False)
                    request_quotation_item.request_quotation = request_quotation
                    request_quotation_item.save()
            
            messages.success(request, "Request quotation was successfully submitted!")
            return redirect('request_quotation_list')
        
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)

    else:
        form = RequestQuotationForm()
        formset = RequestQuotationItemFormSet(queryset=RequestQuotationItem.objects.none())
        
    return render(request, 'create_request_quotation.html', 
        {'form': form, 
         'formset': formset})


@login_required(login_url=settings.LOGIN_URL)
def create_purchase_request(request):
    vat = Decimal('0.00')
    
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            purchase_order = form.save(commit=False)
            purchase_order.total_amount = Decimal('0.00')
            purchase_order.save()

            total_amount = Decimal('0.00')

            for item_form in formset:
                if item_form.cleaned_data:
                    product_name = (
                        item_form.cleaned_data.get('product_name') or
                        item_form.cleaned_data.get('other_product_name')
                    )
                    quantity = item_form.cleaned_data.get('quantity')
                    unit_price = item_form.cleaned_data.get('unit_price')

                    if product_name and unit_price and quantity:
                        total_amount += unit_price * quantity
                        
                        purchase_order_item = item_form.save(commit=False)
                        purchase_order_item.product_name = product_name
                        purchase_order_item.purchase_order = purchase_order
                        purchase_order_item.save()

            vat = total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
            total_amount_with_vat = total_amount + vat

            purchase_order.total_amount = total_amount
            purchase_order.total_amount_with_vat = total_amount_with_vat
            purchase_order.save()

            messages.success(request, "Purchase request was successfully submitted.")
            return redirect('purchase_request_list')

    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet(queryset=PurchaseOrderItem.objects.none())
        
    return render(request, 'create_purchase_request.html', {
        'form': form,
        'formset': formset,
        'vat': vat,
    })



@login_required(login_url=settings.LOGIN_URL)
def request_quotation_list(request):
    due_date = timezone.now().date().strftime('%Y-%m-%d')
    quotations = RequestQuotation.objects.all()

    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]

    return render(request, 'request_quotation_list.html', 
        {'quotations': quotations,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1})


@login_required(login_url=settings.LOGIN_URL)
def request_quotation_detail(request, quotation_id):
    request_quotation = get_object_or_404(RequestQuotation, id=quotation_id)  
    items = request_quotation.items.all()

    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]

    today = date.today()

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(RequestQuotationItem, id=item_id)
        
        if item.price_valid_until and item.price_valid_until <= today:
            return redirect('edit_unit_price_rq', item_id=item.id)

    return render(request, 'request_quotation_detail.html', 
        {'request_quotation': request_quotation,
         'items': items,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'today': today,})


@login_required(login_url=settings.LOGIN_URL)
def edit_unit_price_rq(request, item_id):
    item = get_object_or_404(RequestQuotationItem, id=item_id)

    if request.method == 'POST':
        form = RequestQuotationItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('request_quotation_detail', item.request_quotation.id)
    else:
        form = RequestQuotationItemForm(instance=item)

    return render(request, 'edit_unit_price_rq.html', 
        {'form': form, 
         'item': item})


@login_required(login_url=settings.LOGIN_URL)
def purchase_request_list(request):
    STATUS = os.environ.get('PO_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    purchase_request = PurchaseOrder.objects.all()

    return render(request, 'purchase_request_list.html', 
        {'purchase_request': purchase_request,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def purchase_request_detail(request, pr_id):
    STATUS = os.environ.get('PO_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]
    STATUS_3 = STATUS[3]
    STATUS_4 = STATUS[4] 

    purchase_request = get_object_or_404(PurchaseOrder, id=pr_id)
    print(f"STATUS: {purchase_request.status}")
    vat = purchase_request.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))

    items = purchase_request.items.all()
    for item in items:
        item.total_price = item.unit_price * item.quantity

    number = purchase_request.quotation_no
    quotation_number = number[2:]

    paid_purchase_invoice = PurchaseInvoice.objects.filter(invoice_no__endswith=quotation_number, status="Paid").exists()

    if request.method == "POST":
        print(f"POST: {request.POST}")
        if 'receive' in request.POST:
            purchase_request.status = STATUS_4
            purchase_request.save()
            print(f"Status updated to: {purchase_request.status}")

            for item in items:
                add_or_update_product(
                    product_name=item.product_name,
                    quantity=item.quantity,
                    cost_price=item.unit_price
                )

    return render(request, 'purchase_request_detail.html', 
        {'purchase_request': purchase_request,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2,
         'STATUS_3': STATUS_3,
         'STATUS_4': STATUS_4,
         'vat': vat,
         'items': items,
         'paid_purchase_invoice': paid_purchase_invoice,})


@login_required(login_url=settings.LOGIN_URL)
def view_supplier_quotations(request, quotation_no):
    quotation_number = quotation_no[2:]
    due_date = timezone.now().date().strftime('%Y-%m-%d')
    supplier_quotations = QuotationSubmission.objects.filter(quotation_no__endswith=quotation_number, quote_valid_until__gte=due_date)

    return render(request, 'view_supplier_quotations.html', {'supplier_quotations': supplier_quotations,})


@login_required(login_url=settings.LOGIN_URL)
def supplier_quotation_submission_detail(request, submission_id):
    quotation_submission = get_object_or_404(QuotationSubmission, id=submission_id)
    items = quotation_submission.items.all()

    return render(request, 'supplier_quotation_submission_detail.html', 
        {'quotation_submission': quotation_submission, 
         'items': items})


@login_required(login_url=settings.LOGIN_URL)
def purchase_invoice_list(request):
    purchase_invoices = PurchaseInvoice.objects.all()

    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'purchase_invoice_list.html', 
        {'purchase_invoices': purchase_invoices,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def purchase_invoice_detail(request, pi_id):
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=pi_id)

    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    if request.method == "POST":
        form = PurchaseInvoiceForm(request.POST, instance=purchase_invoice)

        if form.is_valid():
            form.save()

            return redirect('purchase_invoice_detail', pi_id)

    else:
        form = PurchaseInvoiceForm()
    
    return render(request, 'purchase_invoice_detail.html', 
        {'purchase_invoice': purchase_invoice,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2,
         'form': form})