import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import QuotationSubmissionForm, QuotationSubmissionItemFormSet
from .models import QuotationSubmission, QuotationSubmissionItem
from procurement_view.models import RequestQuotation

load_dotenv()


def request_quotations_list(request):
    STATUS = os.environ.get('RQ_STATUS_CHOICES', '').split(',')
    request_quotations = RequestQuotation.objects.filter(status=STATUS[0])

    return render(request, 'request_quotations_list.html', {'request_quotations': request_quotations})

def request_quotations_detail(request, quotation_id):
    quotation = get_object_or_404(RequestQuotation, id=quotation_id)
    return render(request, 'request_quotations_detail.html', {'quotation': quotation})

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