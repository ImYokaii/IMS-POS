from django.urls import path
from . import views


urlpatterns = [
    path('invalid_request/', views.invalid_request, name="invalid_request"),

    path('request_quotations_list/', views.request_quotations_list, name="request_quotations_list"),
    path('request_quotations_detail/<str:signed_id>', views.request_quotations_detail, name="request_quotations_detail"),
    path('download_request_quotations_pdf/<int:quotation_id>', views.download_request_quotations_pdf, name="download_request_quotations_pdf"),

    path('create_quotation_submission/<str:signed_id>', views.create_quotation_submission, name="create_quotation_submission"),
    path('quotation_submission_list/', views.quotation_submission_list, name="quotation_submission_list"),
    path('quotation_submission_detail/<str:signed_id>', views.quotation_submission_detail, name="quotation_submission_detail"),
    path('download_quotation_submission_pdf/<int:quotation_id>', views.download_quotation_submission_pdf, name="download_quotation_submission_pdf"),
    path('edit_unit_price_qs/<str:signed_id>', views.edit_unit_price_qs, name='edit_unit_price_qs'),

    path('purchase_orders_list/', views.purchase_orders_list, name="purchase_orders_list"),
    path('purchase_orders_detail/<str:signed_id>', views.purchase_orders_detail, name="purchase_orders_detail"),
    path('download_purchase_orders_pdf/<int:purchase_order_id>', views.download_purchase_orders_pdf, name="download_purchase_orders_pdf"),

    path('purchase_invoices_list/', views.purchase_invoices_list, name="purchase_invoices_list"),
    path('purchase_invoices_detail/<str:signed_id>', views.purchase_invoices_detail, name="purchase_invoices_detail"),
    path('download_purchase_invoices_pdf/<int:purchase_invoice_id>', views.download_purchase_invoices_pdf, name="download_purchase_invoices_pdf"),
]