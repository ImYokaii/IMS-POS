from django.shortcuts import render, redirect
from .forms import RequestQuotationForm, RequestQuotationItemForm, RequestQuotationItemFormSet
from .models import RequestQuotationItem

# Create your views here.
def create_request_quotation(request):
    if request.method == "POST":
        form1 = RequestQuotationForm(request.POST)
        formset = RequestQuotationItemFormSet(request.POST)

        if form1.is_valid() and formset.is_valid():
            request_quotation = form1.save()

            for form in formset:

                if form.cleaned_data:
                    request_quotation_item = form.save(commit=False)
                    request_quotation_item.request_quotation = request_quotation
                    request_quotation_item.save()

            return redirect("dashboard")

    else:
        form1 = RequestQuotationForm()
        formset = RequestQuotationItemFormSet(queryset=RequestQuotationItem.objects.none())
        
    return render(request, 'create_request_quotation.html', {'form1': form1,'formset': formset})
