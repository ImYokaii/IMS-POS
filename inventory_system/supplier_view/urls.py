from django.urls import path
from . import views


urlpatterns = [
    path('request_quotations_list/', views.request_quotations_list, name="request_quotations_list"),
    path('request_quotations_detail/<int:quotation_id>', views.request_quotations_detail, name="request_quotations_detail"),
    path('create_quotation_submission/<int:quotation_id>', views.create_quotation_submission, name="create_quotation_submission"),
    path('quotation_submission_list/', views.quotation_submission_list, name="quotation_submission_list"),
    path('quotation_submission_detail/<int:qs_id>', views.quotation_submission_detail, name="quotation_submission_detail"),
    path('edit_unit_price_qs/<int:item_id>/', views.edit_unit_price_qs, name='edit_unit_price_qs'),
    path('purchase_orders_list/', views.purchase_orders_list, name="purchase_orders_list"),
    path('purchase_orders_detail/<int:po_id>', views.purchase_orders_detail, name="purchase_orders_detail"),
    path('purchase_invoices_list/', views.purchase_invoices_list, name="purchase_invoices_list"),
    path('purchase_invoices_detail/<int:pi_id>', views.purchase_invoices_detail, name="purchase_invoices_detail"),
    path('generate_invoice_pdf/<int:po_id>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
]