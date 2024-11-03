from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequestQuotationForm, RequestQuotationItemFormSet, PurchaseOrderForm, PurchaseOrderItemFormSet
from .models import RequestQuotation, RequestQuotationItem, PurchaseOrderItem
from django.http import HttpResponse


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
    quotations = RequestQuotation.objects.all()  # Fetch all quotations
    return render(request, 'request_quotation_list.html', {'quotations': quotations})


def request_quotation_detail(request, quotation_id):  
    request_quotation = get_object_or_404(RequestQuotation, id=quotation_id)  
    items = request_quotation.items.all()  # Now this should work

    return render(request, 'request_quotation_detail.html', {
        'request_quotation': request_quotation,
        'items': items
    })