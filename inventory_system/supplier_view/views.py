import os
from dotenv import load_dotenv
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .utils import create_digital_invoice
from .forms import PurchaseOrderStatusForm, QuotationSubmissionForm, QuotationSubmissionItemForm, QuotationSubmissionItemFormSet, PurchaseInvoiceForm
from .models import QuotationSubmission, QuotationSubmissionItem, PurchaseInvoice, PurchaseInvoiceItem
from procurement_view.models import RequestQuotation, RequestQuotationItem, PurchaseOrder, PurchaseOrderItem
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors


load_dotenv()


def request_quotations_list(request):
    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    due_date = timezone.now().date().strftime('%Y-%m-%d')
    request_quotations = RequestQuotation.objects.filter(quote_valid_until__gte=due_date, status=STATUS[0])

    return render(request, 'request_quotations_list.html', {'request_quotations': request_quotations})


def request_quotations_detail(request, quotation_id):
    quotation = get_object_or_404(RequestQuotation, id=quotation_id)
    
    return render(request, 'request_quotations_detail.html', {'quotation': quotation})


def purchase_orders_list(request):
    STATUS = os.environ.get('PO_STATUS_CHOICES', '').split(',')
    purchase_orders = PurchaseOrder.objects.all()

    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'purchase_orders_list.html', 
        {'purchase_orders': purchase_orders,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


def purchase_orders_detail(request, po_id):
    STATUS = os.environ.get('PO_STATUS_CHOICES', '').split(',')
    purchase_order = get_object_or_404(PurchaseOrder, id=po_id)

    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    if request.method == "POST":
        form = PurchaseOrderStatusForm(request.POST, instance=purchase_order)
        if form.is_valid():
            form.save()

            if purchase_order.status == STATUS_1:
                logged_user = request.user
                quotation_no = purchase_order.quotation_no[2:]
                has_pending_submission = PurchaseInvoice.objects.filter(supplier=logged_user, invoice_no__endswith=quotation_no, status__in=["Pending","Paid"]).exists()
                
                if has_pending_submission:
                    messages.error(request, "A digital invoice for this purchase order already exists.")
                
                else:
                    create_digital_invoice(purchase_order)
                    print(f"Purchase Invoice Created: PI{quotation_no}")

            return redirect('purchase_orders_detail', po_id=po_id)
    else:
        form = PurchaseOrderStatusForm(instance=purchase_order)

    return render(request, 'purchase_orders_detail.html', 
        {'purchase_order': purchase_order, 
         'form': form,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2}
        )


def purchase_invoices_list(request):
    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    purchase_invoices = PurchaseInvoice.objects.filter(supplier=request.user)

    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]

    return render(request, 'purchase_invoices_list.html', 
        {'purchase_invoices': purchase_invoices,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


def purchase_invoices_detail(request, pi_id):
    STATUS = os.environ.get('PI_STATUS_CHOICES', '').split(',')
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=pi_id)

    STATUS_0 = STATUS[0]
    STATUS_1 = STATUS[1]
    STATUS_2 = STATUS[2]
    
    return render(request, 'purchase_invoices_detail.html', 
        {'purchase_invoice': purchase_invoice,
         'STATUS_0': STATUS_0,
         'STATUS_1': STATUS_1,
         'STATUS_2': STATUS_2})


def generate_invoice_pdf(request, po_id):
    purchase_invoice = get_object_or_404(PurchaseInvoice, id=po_id)
    items = PurchaseInvoiceItem.objects.filter(purchase_invoice=purchase_invoice)

    # Calculate the total price
    total_amount = sum(item.quantity * item.unit_price for item in items)

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

    pdf_canvas.drawString(4 * inch, 8 * inch, f"Invoice Status: {purchase_invoice.status}")

    # Draw item headers with better alignment
    pdf_canvas.drawString(1 * inch, 7 * inch, "Product Name")
    pdf_canvas.drawString(3 * inch, 7 * inch, "Quantity")
    pdf_canvas.drawString(4.5 * inch, 7 * inch, "Unit Price")
    pdf_canvas.drawString(6 * inch, 7 * inch, "Total Price")
    
    # Draw lines for the item headers
    pdf_canvas.line(1 * inch, 6.8 * inch, 6.8 * inch, 6.8 * inch)

    # Set initial y position for items
    y = 6.5 * inch

    # List each item in the purchase order
    for item in items:
        pdf_canvas.drawString(1 * inch, y, item.product_name)
        pdf_canvas.drawString(3 * inch, y, str(item.quantity))
        pdf_canvas.drawString(4.5 * inch, y, f"${item.unit_price:.2f}")
        pdf_canvas.drawString(6 * inch, y, f"${item.quantity * item.unit_price:.2f}")
        y -= 0.3 * inch  # Move down for the next line

    # Draw lines for each item
    pdf_canvas.line(1 * inch, y + 0.15 * inch, 6.8 * inch, y + 0.15 * inch)

    # Draw the total amount at the bottom
    pdf_canvas.drawString(1 * inch, y - 0.5 * inch, f"Total Amount: ${total_amount:.2f}")

    # Finalize and save PDF
    pdf_canvas.showPage()
    pdf_canvas.save()
    return response


def create_quotation_submission(request, quotation_id):
    quotation_request = get_object_or_404(RequestQuotation, id=quotation_id)
    quotation_request_items = RequestQuotationItem.objects.filter(request_quotation=quotation_request)

    logged_user = request.user
    quotation_no = quotation_request.quotation_no[2:]
    has_pending_submission = QuotationSubmission.objects.filter(supplier=logged_user, quotation_no__endswith=quotation_no, status__in=["Pending","Accepted"]).exists()
    if has_pending_submission:
        messages.error(request, "You have already submitted a quotation submission for this request.")
        return redirect("request_quotations_list")
    
    
    initial_submission_data = {
        'buyer_company_name': quotation_request.buyer_company_name,
        'buyer_address': quotation_request.buyer_address,
        'buyer_contact': quotation_request.buyer_contact,
        'quotation_no': quotation_request.quotation_no,
        'quote_valid_until': quotation_request.quote_valid_until,
    }

    initial_items_data = [
        {
            'product_name': item.product_name,
            'quantity': item.quantity
        }
        for item in quotation_request_items
    ]


    if request.method == "POST":
        form = QuotationSubmissionForm(request.POST, initial=initial_submission_data)
        formset = QuotationSubmissionItemFormSet(request.POST, queryset=QuotationSubmissionItem.objects.none())

        if form.is_valid() and formset.is_valid():
            quotation_submission = form.save(commit=False)
            quotation_submission.quotation_request = quotation_request
            quotation_submission.save()

            for form in formset:
                if form.cleaned_data:
                    quotation_submission_item = form.save(commit=False)
                    quotation_submission_item.quotation_submission = quotation_submission
                    quotation_submission_item.save()

            return redirect('request_quotations_list')
        
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", [f.errors for f in formset.forms])

    else:
        form = QuotationSubmissionForm(initial=initial_submission_data)
        formset = QuotationSubmissionItemFormSet(queryset=QuotationSubmissionItem.objects.none(), initial=initial_items_data)

    return render(request, 'create_quotation_submission.html', {'form': form, 'formset': formset, 'quotation_request': quotation_request, 'quotation_request_items': quotation_request_items})