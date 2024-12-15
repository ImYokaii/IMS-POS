import os
from dotenv import load_dotenv
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .utils import create_digital_invoice
from .forms import QuotationSubmissionForm, QuotationSubmissionItemForm, QuotationSubmissionItemFormSet, EditQuotationPriceForm, PurchaseInvoiceForm
from .models import QuotationSubmission, QuotationSubmissionItem, PurchaseInvoice, PurchaseInvoiceItem
from procurement_view.models import RequestQuotation, RequestQuotationItem, PurchaseOrder, PurchaseOrderItem
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.conf import settings
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.utils import timezone
from datetime import date

load_dotenv()


@login_required(login_url=settings.LOGIN_URL)
def request_quotations_list(request):
    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]

    due_date = timezone.now().date().strftime('%Y-%m-%d')
    request_quotations = RequestQuotation.objects.filter(quote_valid_until__gte=due_date, status=STATUS_0)

    return render(request, 'request_quotations_list.html', 
        {'request_quotations': request_quotations,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,})


@login_required(login_url=settings.LOGIN_URL)
def request_quotations_detail(request, quotation_id):
    quotation = get_object_or_404(RequestQuotation, id=quotation_id)

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
def purchase_orders_list(request):
    purchase_orders = PurchaseOrder.objects.all()

    STATUS = os.environ.get('PO_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'purchase_orders_list.html', 
        {'purchase_orders': purchase_orders,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def purchase_orders_detail(request, po_id):
    STATUS_CHOICES = os.environ.get('PO_STATUS_CHOICES', '').split(',')
    purchase_order = get_object_or_404(PurchaseOrder, id=po_id)

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

        return redirect('purchase_orders_detail', po_id=po_id)

    return render(request, 'purchase_orders_detail.html', {
        'purchase_order': purchase_order,
        'STATUS_CHOICES': STATUS_CHOICES,
        'vat': vat,
        'items': items,
    })


@login_required(login_url=settings.LOGIN_URL)
def purchase_invoices_list(request):
    purchase_invoices = PurchaseInvoice.objects.filter(supplier=request.user)

    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'purchase_invoices_list.html', 
        {'purchase_invoices': purchase_invoices,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def purchase_invoices_detail(request, pi_id):
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=pi_id)

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
            purchase_invoice.save()

        return redirect('purchase_invoices_detail', pi_id=pi_id)

    return render(request, 'purchase_invoices_detail.html',
        {'purchase_invoice': purchase_invoice,
        'STATUS_0': STATUS_0,
        'STATUS_1': STATUS_1,
        'STATUS_2': STATUS_2,
        'vat': vat,
        'items': items,})



@login_required(login_url=settings.LOGIN_URL)
def generate_invoice_pdf(request, po_id):
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=po_id)
    items = PurchaseInvoiceItem.objects.filter(purchase_invoice=purchase_invoice)

    # Calculate total amount and VAT
    total_amount = purchase_invoice.total_amount_payable
    vat_rate = Decimal(float(os.environ.get('VALUE_ADDED_TAX')))  # e.g., 0.12 for 12% VAT
    vat_amount = total_amount * vat_rate
    total_with_vat = purchase_invoice.total_amount_payable_with_vat

    # Set up PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{purchase_invoice.invoice_no}.pdf"'

    # Create PDF document
    pdf_canvas = canvas.Canvas(response, pagesize=A4)
    pdf_canvas.setTitle(f"Invoice for Quotation {purchase_invoice.invoice_no}")

    # Draw a header box
    pdf_canvas.setStrokeColor(colors.black)
    pdf_canvas.setLineWidth(1)
    pdf_canvas.rect(0.5 * inch, 9.5 * inch, 7 * inch, 1 * inch)

    # Write header information with improved spacing
    pdf_canvas.drawString(1 * inch, 10 * inch, f"Invoice for Quotation: {purchase_invoice.invoice_no}")
    
    # General details in two columns
    pdf_canvas.drawString(1 * inch, 9 * inch, f"Supplier: {purchase_invoice.supplier_company_name}")
    pdf_canvas.drawString(4 * inch, 9 * inch, f"Date Issued: {purchase_invoice.date_issued.strftime('%Y-%m-%d')}")
    pdf_canvas.drawString(1 * inch, 8.5 * inch, f"Supplier Address: {purchase_invoice.supplier_address}")
    pdf_canvas.drawString(4 * inch, 8.5 * inch, f"Invoice Status: {purchase_invoice.status}")

    # Draw item headers
    pdf_canvas.drawString(1 * inch, 7 * inch, "Product Name")
    pdf_canvas.drawString(3 * inch, 7 * inch, "Quantity")
    pdf_canvas.drawString(4.5 * inch, 7 * inch, "Unit Price")
    pdf_canvas.drawString(6 * inch, 7 * inch, "Total Price")
    pdf_canvas.line(1 * inch, 6.8 * inch, 6.8 * inch, 6.8 * inch)

    # List items in the purchase order
    y = 6.5 * inch
    for item in items:
        pdf_canvas.drawString(1 * inch, y, item.product_name)
        pdf_canvas.drawString(3 * inch, y, str(item.quantity))
        pdf_canvas.drawString(4.5 * inch, y, f"${item.unit_price:.2f}")
        pdf_canvas.drawString(6 * inch, y, f"${item.quantity * item.unit_price:.2f}")
        y -= 0.3 * inch  # Move down for the next line

    # Draw lines for each item
    pdf_canvas.line(1 * inch, y + 0.15 * inch, 6.8 * inch, y + 0.15 * inch)

    # Add subtotal, VAT, and total with VAT
    y -= 0.5 * inch
    pdf_canvas.drawString(1 * inch, y, f"Subtotal: ${total_amount:.2f}")
    y -= 0.3 * inch
    pdf_canvas.drawString(1 * inch, y, f"VAT ({vat_rate * 100:.0f}%): ${vat_amount:.2f}")
    y -= 0.3 * inch
    pdf_canvas.drawString(1 * inch, y, f"Total (with VAT): ${total_with_vat:.2f}")

    # Finalize and save PDF
    pdf_canvas.showPage()
    pdf_canvas.save()
    return response


@login_required(login_url=settings.LOGIN_URL)
def create_quotation_submission(request, quotation_id):
    quotation_request = get_object_or_404(RequestQuotation, id=quotation_id)
    quotation_request_items = RequestQuotationItem.objects.filter(request_quotation=quotation_request)

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
            quotation_submission.request_quotation = quotation_request
            quotation_submission.save()

            total_amount = 0
            for form in formset:
                if form.cleaned_data:
                    # Skip forms where all relevant fields are None, blank, or null
                    # if not any(value for key, value in form.cleaned_data.items() if key != 'DELETE'):
                    #     continue
                    
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
    quotation_submission = QuotationSubmission.objects.filter(supplier=logged_user)

    STATUS = os.environ.get('QS_STATUS_CHOICES', '').split(',')
    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'quotation_submission_list.html', 
        {'quotation_submission': quotation_submission,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


@login_required(login_url=settings.LOGIN_URL)
def quotation_submission_detail(request, qs_id):
    quotation_submission = get_object_or_404(QuotationSubmission, id=qs_id)

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
            return redirect('edit_unit_price_qs', item_id=item.id)

    return render(request, 'quotation_submission_detail.html', 
        {'quotation_submission': quotation_submission,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2,
         'today': today,
         'items': items,
         'vat': vat,})


@login_required(login_url=settings.LOGIN_URL)
def edit_unit_price_qs(request, item_id):
    item = get_object_or_404(QuotationSubmissionItem, id=item_id)

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
                return redirect('quotation_submission_detail', item.quotation_submission.id)
            
        else:
            messages.error(request, "Please ensure all required fields are correctly filled.")
            
    else:
        form = EditQuotationPriceForm(instance=item)

    return render(request, 'edit_unit_price_qs.html', 
        {'form': form, 
         'item': item})
