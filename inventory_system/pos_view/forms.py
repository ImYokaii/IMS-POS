from django import forms

class ProductSearchForm(forms.Form):
    sku = forms.CharField(label='Search by SKU', required=False)
    name = forms.CharField(label='Search by Product Name', required=False)


class InvoiceSearchForm(forms.Form):
    invoice_no = forms.CharField(label='Search by SKU', required=False)
    receipt_date = forms.DateField(required=False)