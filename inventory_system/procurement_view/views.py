from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequestQuotationForm, RequestQuotationItemFormSet, PurchaseOrderForm, PurchaseOrderItemFormSet
from .models import RequestQuotation, RequestQuotationItem, PurchaseOrderItem
from supplier_view.models import QuotationSubmission, QuotationSubmissionItem
from django.http import HttpResponse
from django.utils import timezone


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
    request.session['can_view_request_quotation_detail'] = True
    request.session['can_view_supplier_quotations'] = True

    due_date = timezone.now().date().strftime('%Y-%m-%d')
    quotations = RequestQuotation.objects.filter(quote_valid_until__gte=due_date)
    return render(request, 'request_quotation_list.html', {'quotations': quotations})


def request_quotation_detail(request, quotation_id):
    if not request.session.get('can_view_request_quotation_detail'):
        return redirect('request_quotation_list')
    
    del request.session['can_view_request_quotation_detail']

    request_quotation = get_object_or_404(RequestQuotation, id=quotation_id)  
    items = request_quotation.items.all()

    return render(request, 'request_quotation_detail.html', {
        'request_quotation': request_quotation,
        'items': items
    })


def view_supplier_quotations(request, quotation_no):
    request.session['can_view_quotation_submission_detail'] = True

    if not request.session.get('can_view_supplier_quotations'):
        if not request.session.get('can_go_back_supplier_quotations'):
            return redirect('request_quotation_list')
        
        del request.session['can_go_back_supplier_quotations']
    
    else:
        del request.session['can_view_supplier_quotations']

    
    quotation_no_numeric = quotation_no[2:]
    due_date = timezone.now().date().strftime('%Y-%m-%d')
    supplier_quotations = QuotationSubmission.objects.filter(quotation_no__endswith=quotation_no_numeric, quote_valid_until__gte=due_date)

    return render(request, 'view_supplier_quotations.html', {'supplier_quotations': supplier_quotations,})


def view_quotation_submission_detail(request, submission_id):
    request.session['can_go_back_supplier_quotations'] = True

    if not request.session.get('can_view_quotation_submission_detail'):
        return redirect('request_quotation_list')
    
    del request.session['can_view_quotation_submission_detail']

    quotation_submission = get_object_or_404(QuotationSubmission, id=submission_id)
    items = quotation_submission.items.all()

    return render(request, 'quotation_submission_detail.html', {'quotation_submission': quotation_submission, 'items': items})