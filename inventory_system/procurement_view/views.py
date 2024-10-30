from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequestQuotationForm, RequestQuotationItemFormSet, QuotationSubmissionForm, QuotationSubmissionItemFormSet, PurchaseOrderForm, PurchaseOrderItemFormSet
from .models import RequestQuotation, RequestQuotationItem, QuotationSubmission, QuotationSubmissionItem, PurchaseOrder, PurchaseOrderItem
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def create_request_quotation(request):
    if request.method == "POST":
        form = RequestQuotationForm(request.POST)
        formset = RequestQuotationItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            request_quotation = form.save()

            for form in formset:
                if form.cleaned_data:
                    request_quotation_item = form.save(commit=False)
                    request_quotation_item.request_quotation = request_quotation
                    request_quotation_item.save()

            return redirect('request_quotation_list')

    else:
        form = RequestQuotationForm()
        formset = RequestQuotationItemFormSet(queryset=RequestQuotationItem.objects.none())
        
    return render(request, 'create_request_quotation.html', {'form': form, 'formset': formset})


def create_quotation_submission(request):
    if request.method == "POST":
        form = QuotationSubmissionForm(request.POST)
        formset = QuotationSubmissionItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            quotation_submission = form.save()

            for form in formset:
                if form.cleaned_data:
                    quotation_submission_item = form.save(commit=False)
                    quotation_submission_item.quotation_submission = quotation_submission
                    quotation_submission_item.save()

            return redirect('request_quotation_list')
        
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", [f.errors for f in formset.forms])

    else:
        form = QuotationSubmissionForm()
        formset = QuotationSubmissionItemFormSet(queryset=QuotationSubmissionItem.objects.none())
        
    return render(request, 'create_quotation_submission.html', {'form': form, 'formset': formset})


def create_purchase_request(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            purchase_order = form.save()

            for form in formset:
                if form.cleaned_data:
                    purchase_order_item = form.save(commit=False)
                    purchase_order_item.purchase_order = purchase_order
                    purchase_order_item.save()

            return redirect('request_quotation_list')
        
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", [f.errors for f in formset.forms])

    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet(queryset=PurchaseOrderItem.objects.none())
        
    return render(request, 'create_purchase_request.html', {'form': form, 'formset': formset})


def request_quotation_list(request):
    quotations = RequestQuotation.objects.all()  # Fetch all quotations
    return render(request, 'request_quotation_list.html', {'quotations': quotations})


def request_quotation_detail(request, quotation_id):  
    request_quotation = get_object_or_404(RequestQuotation, id=quotation_id)  
    items = request_quotation.items.all()  # Now this should work

    return render(request, 'request_quotation_detail.html', {
        'request_quotation': request_quotation,
        'items': items
    })


def generate_invoice_pdf(request, quotation_id):
    # Retrieve the specified quotation and its items
    quotation = get_object_or_404(RequestQuotation, id=quotation_id)
    items = RequestQuotationItem.objects.filter(request_quotation=quotation)
    
    # Calculate the total price
    total_amount = sum(item.quantity * item.unit_price for item in items)

    # Set up PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{quotation.quotation_no}.pdf"'
    
    # Create PDF document
    pdf_canvas = canvas.Canvas(response, pagesize=A4)
    pdf_canvas.setTitle(f"Invoice for Quotation {quotation.quotation_no}")

    # Write header information
    pdf_canvas.drawString(1 * inch, 10 * inch, f"Invoice for Quotation: {quotation.quotation_no}")
    pdf_canvas.drawString(1 * inch, 9.5 * inch, f"Buyer: {quotation.buyer_company_name}")
    pdf_canvas.drawString(1 * inch, 9 * inch, f"Prepared By: {quotation.prepared_by}")
    
    # Draw item headers
    pdf_canvas.drawString(1 * inch, 8.5 * inch, "Product Name")
    pdf_canvas.drawString(3 * inch, 8.5 * inch, "Quantity")
    pdf_canvas.drawString(4.5 * inch, 8.5 * inch, "Unit Price")
    pdf_canvas.drawString(6 * inch, 8.5 * inch, "Total Price")
    
    # List each item in the quotation
    y = 8 * inch
    for item in items:
        pdf_canvas.drawString(1 * inch, y, item.product_name)
        pdf_canvas.drawString(3 * inch, y, str(item.quantity))
        pdf_canvas.drawString(4.5 * inch, y, f"${item.unit_price:.2f}")
        pdf_canvas.drawString(6 * inch, y, f"${item.quantity * item.unit_price:.2f}")
        y -= 0.3 * inch  # Move down for the next line
    
    # Draw the total amount at the bottom
    pdf_canvas.drawString(1 * inch, y - 0.5 * inch, f"Total Amount: ${total_amount:.2f}")
    
    # Finalize and save PDF
    pdf_canvas.showPage()
    pdf_canvas.save()
    return response