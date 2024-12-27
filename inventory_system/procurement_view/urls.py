from django.urls import path
from . import views

urlpatterns = [
    path('invalid_request/', views.invalid_request, name="invalid_request"),

    path('create_request_quotation/', views.create_request_quotation, name="create_request_quotation"),
    path('accepted_quotations_list/', views.accepted_quotations_list, name="accepted_quotations_list"),
    
    path('create_purchase_request_from_quotation/<str:signed_id>/', views.create_purchase_request_from_quotation, name='create_purchase_request_from_quotation'),
    path('request_quotation_list/', views.request_quotation_list, name="request_quotation_list"),  
    path('request_quotation_detail/<str:signed_id>/', views.request_quotation_detail, name="request_quotation_detail"),
    path('download_request_quotation_pdf/<int:quotation_id>', views.download_request_quotation_pdf, name="download_request_quotation_pdf"),
    path('edit_unit_price_rq/<str:signed_id>/', views.edit_unit_price_rq, name='edit_unit_price_rq'),
    
    path('view_supplier_quotations/<str:signed_id>/', views.view_supplier_quotations, name="view_supplier_quotations"),
    path('supplier_quotation_submission_detail/<str:signed_id>/', views.supplier_quotation_submission_detail, name="supplier_quotation_submission_detail"),
    path('download_supplier_quotation_pdf/<int:quotation_id>', views.download_supplier_quotation_pdf, name="download_supplier_quotation_pdf"),

    path('purchase_request_list/', views.purchase_request_list, name="purchase_request_list"),
    path('purchase_request_detail/<str:signed_id>', views.purchase_request_detail, name="purchase_request_detail"),
    path('download_purchase_order_pdf/<int:purchase_order_id>', views.download_purchase_order_pdf, name="download_purchase_order_pdf"),

    path('purchase_invoice_list/', views.purchase_invoice_list, name="purchase_invoice_list"),
    path('purchase_invoice_detail/<str:signed_id>/', views.purchase_invoice_detail, name="purchase_invoice_detail"),
    path('download_purchase_invoice_pdf/<int:purchase_invoice_id>', views.download_purchase_invoice_pdf, name="download_purchase_invoice_pdf"),
]
