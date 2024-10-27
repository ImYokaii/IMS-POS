from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequestQuotationForm, RequestQuotationItemFormSet, QuotationSubmissionForm, QuotationSubmissionItemFormSet
from .models import RequestQuotation, RequestQuotationItem, QuotationSubmission, QuotationSubmissionItem

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

            # Redirect to the list view after saving
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

            # Redirect to the list view after saving
            return redirect('request_quotation_list')
        
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", [f.errors for f in formset.forms])

    else:
        form = QuotationSubmissionForm()
        formset = QuotationSubmissionItemFormSet(queryset=QuotationSubmissionItem.objects.none())
        
    return render(request, 'create_quotation_submission.html', {'form': form, 'formset': formset})

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