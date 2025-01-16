import os
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequestQuotationForm, RequestQuotationItemForm, RequestQuotationItemFormSet, EditQuotationPriceForm, PurchaseOrderForm, PurchaseOrderItemFormSet, PurchaseInvoiceForm
from .models import RequestQuotation, RequestQuotationItem, PurchaseOrder, PurchaseOrderItem
from .utils import add_or_update_product
from login_view.models import CompanyProfile
from supplier_view.models import QuotationSubmission, QuotationSubmissionItem, PurchaseInvoice, PurchaseInvoiceItem
from django.http import HttpResponse
from django.utils import timezone
from datetime import date
from decimal import Decimal
from dotenv import load_dotenv
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.paginator import Paginator
from .utils import sign_id, unsign_id


load_dotenv()

@login_required(login_url="/login/")
def invalid_request(request):
    return render(request, 'invalid_request.html')


@login_required(login_url=settings.LOGIN_URL)
def accepted_quotations_list(request):
    due_date = timezone.now().date().strftime('%Y-%m-%d')
    accepted_quotations = QuotationSubmission.objects.filter(status="Accepted", quote_valid_until__gt=due_date).order_by('-quotation_no')

    for quotation in accepted_quotations:
        quotation.signed_id = sign_id(quotation.id)

    paginator = Paginator(accepted_quotations, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'accepted_quotations_list.html', {
        'page_obj': page_obj,
    })


@login_required(login_url=settings.LOGIN_URL)
def create_purchase_request_from_quotation(request, signed_id):
    quotation_id = unsign_id(signed_id)
    if quotation_id is None:
        return redirect("invalid_request")

    quotation_submission = get_object_or_404(QuotationSubmission, id=quotation_id)

    due_date = timezone.now().date()
    if quotation_submission.quote_valid_until <= due_date:
        return redirect('invalid_request')
    
    items = quotation_submission.items.all()
    supplier = CompanyProfile.objects.get(user=quotation_submission.supplier)

    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        quantities = request.POST.getlist('quantity')

        if form.is_valid():
            purchase_order = form.save(commit=False)
            purchase_order.supplier = quotation_submission.supplier
            purchase_order.prepared_by = request.user

            purchase_order.supplier_company_name = supplier.company_name
            purchase_order.supplier_company_address = supplier.company_address
            purchase_order.supplier_company_contact = supplier.company_contact

            purchase_order.total_amount = 0
            
            purchase_order.save()

            for index, item in enumerate(items):
                quantity = int(quantities[index])
                total_item_price = quantity * item.unit_price
                purchase_order.total_amount += total_item_price

                PurchaseOrderItem.objects.create(
                    purchase_order=purchase_order,
                    product_name=item.product_name,
                    quantity=quantity,
                    measurement=item.measurement,
                    unit_price=item.unit_price,
                )

            vat = purchase_order.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
            purchase_order.total_amount_with_vat = purchase_order.total_amount + vat
            purchase_order.save()

            messages.success(request, "Purchase request created successfully.")
            return redirect('purchase_request_list')
        
        else:
            print("Form Errors:", form.errors)

    else:
        form = PurchaseOrderForm(initial={
            'buyer_contact': quotation_submission.buyer_contact,
            'buyer_company_name': quotation_submission.buyer_company_name,
            'buyer_address': quotation_submission.buyer_address,
        })

    return render(request, 'create_purchase_request_from_quotation.html', {
        'form': form,
        'items': items,
        'quotation_submission': quotation_submission,
    })


@login_required(login_url=settings.LOGIN_URL)
def create_request_quotation(request):
    if request.method == "POST":
        form = RequestQuotationForm(request.POST)
        formset = RequestQuotationItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            has_valid_formset_data = any(form.cleaned_data for form in formset)

            if not has_valid_formset_data:
                messages.error(request, "At least one item must be added to the quotation.")
                return redirect('create_request_quotation')
            
            request_quotation = form.save(commit=False)
            request_quotation.employee = request.user
            request_quotation = form.save()

            total_amount = Decimal('0.00')

            for form in formset:
                if form.cleaned_data:
                    product_name = (form.cleaned_data.get('product_name') or form.cleaned_data.get('other_product_name'))
                    
                    request_quotation_item = form.save(commit=False)
                    request_quotation_item.request_quotation = request_quotation
                    request_quotation_item.product_name = product_name
                    request_quotation_item.save()

                    total_amount += request_quotation_item.quantity * request_quotation_item.unit_price
            
            vat = total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
            total_amount_with_vat = total_amount + vat

            request_quotation.total_amount = total_amount
            request_quotation.total_amount_with_vat = total_amount_with_vat
            request_quotation.save()

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
def request_quotation_list(request):
    due_date = timezone.now().date().strftime('%Y-%m-%d')
    request_quotations = RequestQuotation.objects.all()
    quotations = request_quotations.order_by('-quotation_no')

    for quotation in quotations:
        quotation.signed_id = sign_id(quotation.id)

    paginator = Paginator(quotations, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]

    return render(request, 'request_quotation_list.html', 
        {'page_obj': page_obj,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1})


@login_required(login_url=settings.LOGIN_URL)
def request_quotation_detail(request, signed_id):
    quotation_id = unsign_id(signed_id)
    if quotation_id is None:
        return redirect("invalid_request")
    
    request_quotation = get_object_or_404(RequestQuotation, id=quotation_id)
    items = request_quotation.items.all()

    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]

    today = date.today()

    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = request_quotation.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(RequestQuotationItem, id=item_id)
        
        if item.price_valid_until and item.price_valid_until <= today:
            return redirect('edit_unit_price_rq', signed_id=signed_id)

    return render(request, 'request_quotation_detail.html', 
        {'request_quotation': request_quotation,
         'items': items,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'today': today,
         'vat': vat,})


@login_required(login_url=settings.LOGIN_URL)
def download_request_quotation_pdf(request, quotation_id):
    request_quotation = get_object_or_404(RequestQuotation, id=quotation_id)
    items = request_quotation.items.all()

    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = request_quotation.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    context = {
        'request_quotation': request_quotation,
        'items': items,
        'vat': vat,
        'today': date.today(),
    }

    template = get_template('download_request_quotation_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="request-quotation_{request_quotation.quotation_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required(login_url=settings.LOGIN_URL)
def edit_unit_price_rq(request, signed_id):
    item_id = unsign_id(signed_id)
    if item_id is None:
        return redirect("invalid_request")
        
    item = get_object_or_404(RequestQuotationItem, id=item_id)

    if request.method == 'POST':
        form = EditQuotationPriceForm(request.POST, instance=item)

        if form.is_valid():
            unit_price = form.cleaned_data.get('unit_price')
            price_valid_until = form.cleaned_data.get('price_valid_until')

            if price_valid_until and price_valid_until == date.today():
                messages.error(request, "The 'price valid until' date cannot be today's date.")

            elif item.unit_price != unit_price and not price_valid_until:
                messages.error(request, "You must provide a 'price valid until' date when updating the unit price.")

            else:
                form.save()
                messages.success(request, "Unit price and validity date updated successfully.")
                return redirect('request_quotation_detail', signed_id)
        
        else:
            messages.error(request, "Please ensure all required fields are correctly filled.")
            
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

    purchase_request = PurchaseOrder.objects.all().order_by('-quotation_no')

    for quotation in purchase_request:
        quotation.signed_id = sign_id(quotation.id)

    paginator = Paginator(purchase_request, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'purchase_request_list.html', 
        {'page_obj': page_obj,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def purchase_request_detail(request, signed_id):
    pr_id = unsign_id(signed_id)
    if pr_id is None:
        return redirect("invalid_request")

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

    paid_purchase_invoice = PurchaseInvoice.objects.filter(purchase_order=purchase_request, status="Paid").exists()

    if request.method == "POST":
        if 'receive' in request.POST:
            purchase_request.status = STATUS_4
            purchase_request.save()

            for item in items:
                product_name = item.product_name
                quantity = item.quantity
                cost_price = item.unit_price
                add_or_update_product(product_name, quantity, cost_price)
        
        return redirect('purchase_request_detail', signed_id)

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
def download_purchase_order_pdf(request, purchase_order_id):
    purchase_order = get_object_or_404(PurchaseOrder, id=purchase_order_id)
    items = purchase_order.items.all()

    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = purchase_order.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    context = {
        'purchase_order': purchase_order,
        'items': items,
        'vat': vat,
        'today': date.today(),
    }

    template = get_template('download_purchase_order_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="purchase-order_{purchase_order.quotation_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required(login_url=settings.LOGIN_URL)
def view_supplier_quotations(request, signed_id):
    quotation_id = unsign_id(signed_id)
    if quotation_id is None:
        return redirect("invalid_request")
    
    due_date = timezone.now().date().strftime('%Y-%m-%d')
    
    try:
        request_quotation = RequestQuotation.objects.get(id=quotation_id, quote_valid_until__lte=due_date)
    except RequestQuotation.DoesNotExist:
        request_quotation = None

    supplier_quotations = QuotationSubmission.objects.filter(request_quotation=request_quotation, quote_valid_until__gte=due_date).order_by('-quotation_no')

    for quotation in supplier_quotations:
        quotation.signed_id = sign_id(quotation.id)

    paginator = Paginator(supplier_quotations, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_supplier_quotations.html',
        {'page_obj': page_obj,})


@login_required(login_url=settings.LOGIN_URL)
def supplier_quotation_submission_detail(request, signed_id):
    submission_id = unsign_id(signed_id)
    if submission_id is None:
        return redirect("invalid_request")
    
    quotation_submission = get_object_or_404(QuotationSubmission, id=submission_id)

    due_date = timezone.now().date()
    if quotation_submission.request_quotation.quote_valid_until > due_date:
        return redirect('invalid_request')

    items = quotation_submission.items.all()

    quotation_submission.request_quotation.signed_id = sign_id(quotation_submission.request_quotation.id)

    STATUS = os.environ.get('QS_STATUS_CHOICES').split(',')

    PENDING_STATUS = STATUS[0]
    ACCEPTED_STATUS = STATUS[1]
    REJECTED_STATUS = STATUS[2]

    vat = quotation_submission.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))

    for item in items:
        item.total_price = item.unit_price * item.quantity

    if request.method == "POST":
        if 'accept' in request.POST:
            quotation_submission.status = ACCEPTED_STATUS
            quotation_submission.save()
        elif 'reject' in request.POST:
            quotation_submission.status = REJECTED_STATUS
            quotation_submission.save()

        return redirect('supplier_quotation_submission_detail', signed_id)

    return render(request, 'supplier_quotation_submission_detail.html', 
        {'quotation_submission': quotation_submission, 
         'items': items,
         'PENDING_STATUS': PENDING_STATUS,
         'ACCEPTED_STATUS': ACCEPTED_STATUS,
         'REJECTED_STATUS': REJECTED_STATUS,
         'vat': vat,})


@login_required(login_url=settings.LOGIN_URL)
def download_supplier_quotation_pdf(request, quotation_id):
    supplier_quotation = get_object_or_404(QuotationSubmission, id=quotation_id)
    items = supplier_quotation.items.all()

    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = supplier_quotation.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    context = {
        'supplier_quotation': supplier_quotation,
        'items': items,
        'vat': vat,
        'today': date.today(),
    }

    template = get_template('download_supplier_quotation_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="supplier-quotation_{supplier_quotation.quotation_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required(login_url=settings.LOGIN_URL)
def purchase_invoice_list(request):
    purchase_invoices = PurchaseInvoice.objects.all().order_by('-invoice_no')

    for invoice in purchase_invoices:
        invoice.signed_id = sign_id(invoice.id)

    paginator = Paginator(purchase_invoices, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'purchase_invoice_list.html', 
        {'page_obj': page_obj,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def purchase_invoice_detail(request, signed_id):
    pi_id = unsign_id(signed_id)
    if pi_id is None:
        return redirect("invalid_request")
    
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=pi_id)
    items = purchase_invoice.items.all()

    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = purchase_invoice.total_amount_payable * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))

    if request.method == "POST":
        form = PurchaseInvoiceForm(request.POST, instance=purchase_invoice)

        if form.is_valid():
            form.save()

            return redirect('purchase_invoice_detail', signed_id)

    else:
        form = PurchaseInvoiceForm()
    
    return render(request, 'purchase_invoice_detail.html', 
        {'purchase_invoice': purchase_invoice,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2,
         'form': form,
         'items': items,
         'vat': vat,})


@login_required(login_url=settings.LOGIN_URL)
def download_purchase_invoice_pdf(request, purchase_invoice_id):
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=purchase_invoice_id)
    items = purchase_invoice.items.all()

    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = purchase_invoice.total_amount_payable * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    context = {
        'purchase_invoice': purchase_invoice,
        'items': items,
        'vat': vat,
        'today': date.today(),
    }

    template = get_template('download_purchase_invoice_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="purchase-invoice_{purchase_invoice.invoice_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response