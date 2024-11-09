from django.urls import path
from . import views


urlpatterns = [
    path('request_quotations_list/', views.request_quotations_list, name="request_quotations_list"),
    path('request_quotations_detail/<int:quotation_id>', views.request_quotations_detail, name="request_quotations_detail"),
    path('create_quotation_submission/<int:quotation_id>', views.create_quotation_submission, name="create_quotation_submission"),
    path('purchase_orders_list/', views.purchase_orders_list, name="purchase_orders_list"),
    path('purchase_orders_detail/<int:po_id>', views.purchase_orders_detail, name="purchase_orders_detail"),
    path('purchase_invoices_list/', views.purchase_invoices_list, name="purchase_invoices_list"),
    path('purchase_invoices_detail/<int:pi_id>', views.purchase_invoices_detail, name="purchase_invoices_detail"),
    path('generate_invoice_pdf/<int:po_id>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
]