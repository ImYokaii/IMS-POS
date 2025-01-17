import os
from io import BytesIO
from dotenv import load_dotenv
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .utils import create_digital_invoice, sign_id, unsign_id
from .forms import QuotationSubmissionForm, QuotationSubmissionItemForm, QuotationSubmissionItemFormSet, EditQuotationPriceForm, PurchaseInvoiceForm
from .models import QuotationSubmission, QuotationSubmissionItem, PurchaseInvoice, PurchaseInvoiceItem
from procurement_view.models import RequestQuotation, RequestQuotationItem, PurchaseOrder, PurchaseOrderItem
from login_view.models import CompanyProfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.conf import settings
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.utils import timezone
from datetime import date
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.paginator import Paginator


load_dotenv()


@login_required(login_url=settings.LOGIN_URL)
def invalid_request(request):
    return render(request, 'invalid_request.html')


@login_required(login_url=settings.LOGIN_URL)
def request_quotations_list(request):
    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]

    due_date = timezone.now().date().strftime('%Y-%m-%d')
    request_quotations = RequestQuotation.objects.filter(quote_valid_until__gt=due_date).order_by('-quotation_no')

    for quotation in request_quotations:
        quotation.signed_id = sign_id(quotation.id)

    paginator = Paginator(request_quotations, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'request_quotations_list.html', 
        {'page_obj': page_obj,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,})


@login_required(login_url=settings.LOGIN_URL)
def request_quotations_detail(request, signed_id):
    quotation_id = unsign_id(signed_id)
    if quotation_id is None:
        return redirect("invalid_request")
    
    quotation = get_object_or_404(RequestQuotation, id=quotation_id)

    due_date = timezone.now().date()
    if quotation.quote_valid_until <= due_date:
        return redirect('invalid_request')

    quotation.signed_id = sign_id(quotation.id)

    items = quotation.items.all()
    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = quotation.total_amount * (Decimal(float(os.environ.get('VALUE_ADDED_TAX'))))
    print("VAT: ", vat)

    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    
    return render(request, 'request_quotations_detail.html', 
        {'quotation': quotation,
         'items': items,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'vat': vat,})


@login_required(login_url=settings.LOGIN_URL)
def download_request_quotations_pdf(request, quotation_id):
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

    template = get_template('download_request_quotations_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="request-quotation_{request_quotation.quotation_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required(login_url=settings.LOGIN_URL)
def purchase_orders_list(request):
    purchase_orders = PurchaseOrder.objects.filter(supplier=request.user).order_by('-quotation_no')

    for quotation in purchase_orders:
        quotation.signed_id = sign_id(quotation.id)

    paginator = Paginator(purchase_orders, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    STATUS = os.environ.get('PO_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'purchase_orders_list.html', 
        {'page_obj': page_obj,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def purchase_orders_detail(request, signed_id):
    po_id = unsign_id(signed_id)
    if po_id is None:
        return redirect("invalid_request")

    STATUS_CHOICES = os.environ.get('PO_STATUS_CHOICES', '').split(',')
    purchase_order = get_object_or_404(PurchaseOrder, id=po_id)

    if purchase_order.supplier != request.user:
        return redirect('invalid_request')

    vat = purchase_order.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))

    items = purchase_order.items.all()
    for item in items:
        item.total_price = item.unit_price * item.quantity

    if request.method == "POST":
        if 'approve' in request.POST:
            purchase_order.status = "Approved"
        elif 'reject' in request.POST:
            purchase_order.status = "Rejected"
        elif 'deliver' in request.POST:
            purchase_order.status = "Delivered"
            create_digital_invoice(purchase_order)
        elif 'cancel' in request.POST:
            purchase_order.status = "Cancelled"

        purchase_order.save()

        if purchase_order.status == "Approved":
            logged_user = request.user
            has_pending_submission = PurchaseInvoice.objects.filter(
                purchase_order=purchase_order,
                supplier=logged_user,
                status__in=["Pending", "Paid"]
            ).exists()

            if has_pending_submission:
                messages.error(request, "A digital invoice for this purchase order already exists.")  

        return redirect('purchase_orders_detail', signed_id)

    return render(request, 'purchase_orders_detail.html', {
        'purchase_order': purchase_order,
        'STATUS_CHOICES': STATUS_CHOICES,
        'vat': vat,
        'items': items,
    })


@login_required(login_url=settings.LOGIN_URL)
def download_purchase_orders_pdf(request, purchase_order_id):
    purchase_order = get_object_or_404(PurchaseOrder, id=purchase_order_id)

    if purchase_order.supplier != request.user:
        return redirect('invalid_request')
    
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

    template = get_template('download_purchase_orders_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="purchase-order_{purchase_order.quotation_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required(login_url=settings.LOGIN_URL)
def purchase_invoices_list(request):
    purchase_invoices = PurchaseInvoice.objects.filter(supplier=request.user).order_by('-invoice_no')

    for invoice in purchase_invoices:
        invoice.signed_id = sign_id(invoice.id)

    paginator = Paginator(purchase_invoices, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'purchase_invoices_list.html', 
        {'page_obj': page_obj,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def purchase_invoices_detail(request, signed_id):
    pi_id = unsign_id(signed_id)
    if pi_id is None:
        return redirect("invalid_request")
    
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=pi_id)

    if purchase_invoice.supplier != request.user:
        return redirect('invalid_request')

    vat = purchase_invoice.total_amount_payable * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))

    items = purchase_invoice.items.all()
    for item in items:
        item.total_price = item.unit_price * item.quantity

    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    if request.method == "POST":
        if 'paid' in request.POST:
            purchase_invoice.status = STATUS_1
            purchase_invoice.save()
        elif 'voided' in request.POST:
            purchase_invoice.status = STATUS_2
            purchase_order = purchase_invoice.purchase_order
            purchase_order.status = "Cancelled"
            purchase_invoice.save()
            purchase_order.save()

        return redirect('purchase_invoices_detail', signed_id)

    return render(request, 'purchase_invoices_detail.html',
        {'purchase_invoice': purchase_invoice,
        'STATUS_0': STATUS_0,
        'STATUS_1': STATUS_1,
        'STATUS_2': STATUS_2,
        'vat': vat,
        'items': items,})


@login_required(login_url=settings.LOGIN_URL)
def download_purchase_invoices_pdf(request, purchase_invoice_id):
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=purchase_invoice_id)

    if purchase_invoice.supplier != request.user:
        return redirect('invalid_request')
    
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

    template = get_template('download_purchase_invoices_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="purchase-invoice_{purchase_invoice.invoice_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required(login_url=settings.LOGIN_URL)
def create_quotation_submission(request, signed_id):
    quotation_id = unsign_id(signed_id)
    if quotation_id is None:
        return redirect("invalid_request")

    quotation_request = get_object_or_404(RequestQuotation, id=quotation_id)
    quotation_request_items = RequestQuotationItem.objects.filter(request_quotation=quotation_request)
    supplier = CompanyProfile.objects.get(user=request.user)

    logged_user = request.user
    has_pending_submission = QuotationSubmission.objects.filter(
        supplier=logged_user, request_quotation=quotation_request, status__in=["Pending", "Accepted"]
    ).exists()
    if has_pending_submission:
        messages.error(request, "You have already submitted a quotation submission for this request.")
        return redirect("request_quotations_list")

    initial_items_data = [
        {
            'product_name': item.product_name,
            'quantity': item.quantity,
            'measurement': item.measurement,
            'unit_price': '',
            'price_valid_until': '',
        }
        for item in quotation_request_items
    ]

    if request.method == "POST":
        form = QuotationSubmissionForm(request.POST)
        formset = QuotationSubmissionItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            quotation_submission = form.save(commit=False)
            quotation_submission.supplier = request.user
            quotation_submission.supplier_company_name = supplier.company_name
            quotation_submission.supplier_company_address = supplier.company_address
            quotation_submission.supplier_company_contact = supplier.company_contact
            quotation_submission.request_quotation = quotation_request
            quotation_submission.save()

            total_amount = 0
            for form in formset:
                if form.cleaned_data:
                    quotation_submission_item = form.save(commit=False)
                    quotation_submission_item.quotation_submission = quotation_submission
                    quotation_submission_item.save()
            
                    total_amount += quotation_submission_item.quantity * quotation_submission_item.unit_price

            quotation_submission.total_amount = total_amount
            vat = total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
            quotation_submission.total_amount_with_vat = total_amount + vat
            quotation_submission.save()

            messages.success(request, "Quotation was successfully submitted!")
            return redirect('quotation_submission_list')

        else:
            print("Form errors:", form.errors)
            print("Formset errors:", [f.errors for f in formset.forms])

    else:
        form = QuotationSubmissionForm()
        formset = QuotationSubmissionItemFormSet(queryset=QuotationSubmissionItem.objects.none(), initial=initial_items_data)

    return render(request, 'create_quotation_submission.html', {
        'form': form,
        'formset': formset,
        'quotation_request': quotation_request,
        'quotation_request_items': quotation_request_items,
    })


@login_required(login_url=settings.LOGIN_URL)
def quotation_submission_list(request):
    logged_user = request.user
    quotation_submission = QuotationSubmission.objects.filter(supplier=logged_user).order_by('-quotation_no')

    for quotation in quotation_submission:
        quotation.signed_id = sign_id(quotation.id)

    paginator = Paginator(quotation_submission, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    STATUS = os.environ.get('QS_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'quotation_submission_list.html', 
        {'page_obj': page_obj,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def quotation_submission_detail(request, signed_id):
    qs_id = unsign_id(signed_id)
    if qs_id is None:
        return redirect("invalid_request")
    
    quotation_submission = get_object_or_404(QuotationSubmission, id=qs_id)

    if quotation_submission.supplier != request.user:
        return redirect('invalid_request')

    STATUS = os.environ.get('QS_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    today = date.today()

    items = quotation_submission.items.all()
    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = quotation_submission.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(QuotationSubmissionItem, id=item_id)
        
        if item.price_valid_until and item.price_valid_until <= today:
            return redirect('edit_unit_price_qs', signed_id)

    return render(request, 'quotation_submission_detail.html', 
        {'quotation_submission': quotation_submission,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2,
         'today': today,
         'items': items,
         'vat': vat,})


@login_required(login_url=settings.LOGIN_URL)
def download_quotation_submission_pdf(request, quotation_id):
    quotation_submission = get_object_or_404(QuotationSubmission, id=quotation_id)

    if quotation_submission.supplier != request.user:
        return redirect('invalid_request')
    
    items = quotation_submission.items.all()

    for item in items:
        item.total_price = item.unit_price * item.quantity

    vat = quotation_submission.total_amount * Decimal(float(os.environ.get('VALUE_ADDED_TAX')))
    context = {
        'quotation_submission': quotation_submission,
        'items': items,
        'vat': vat,
        'today': date.today(),
    }

    template = get_template('download_quotation_submission_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quotation-submission_{quotation_submission.quotation_no}.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required(login_url=settings.LOGIN_URL)
def edit_unit_price_qs(request, signed_id):
    item_id = unsign_id(signed_id)
    if item_id is None:
        return redirect("invalid_request")
    
    item = get_object_or_404(QuotationSubmissionItem, id=item_id)

    if item.quotation_submission.supplier != request.user:
        return redirect('invalid_request')

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
                return redirect('quotation_submission_detail', signed_id)
            
        else:
            messages.error(request, "Please ensure all required fields are correctly filled.")
            
    else:
        form = EditQuotationPriceForm(instance=item)

    return render(request, 'edit_unit_price_qs.html', 
        {'form': form, 
         'item': item})