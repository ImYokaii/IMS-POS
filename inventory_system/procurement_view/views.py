from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequestQuotationForm, RequestQuotationItemFormSet
from .models import RequestQuotation, RequestQuotationItem

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

            # Redirect to the detail view after saving
            return redirect('request_quotation_detail', request_quotation.id)

    else:
        form = RequestQuotationForm()
        formset = RequestQuotationItemFormSet(queryset=RequestQuotationItem.objects.none())
        
    return render(request, 'create_request_quotation.html', {'form': form, 'formset': formset})

def request_quotation_detail(request, quotation_id):
    request_quotation = get_object_or_404(RequestQuotation, id=quotation_id)
    items = request_quotation.items.all()  # Get all related items
    return render(request, 'request_quotation_detail.html', {'request_quotation': request_quotation, 'items': items})

def invoice_generation(request):
    return render(request, 'invoice_generation.html')

def request_quotation_list(request):
    quotations = RequestQuotation.objects.all()  # Fetch all quotations
    return render(request, 'request_quotation_list.html', {'quotations': quotations})
