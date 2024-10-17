from django.shortcuts import render, redirect
from .forms import RequestQuotationForm

# Create your views here.
def create_request_quotation(request):
    if request.method == "POST":
        form = RequestQuotationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:
        form = RequestQuotationForm()
        
    return render(request, 'create_request_quotation.html', {'form': form})