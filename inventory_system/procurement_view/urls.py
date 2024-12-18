from django.urls import path
from . import views

urlpatterns = [
    path('create_request_quotation/', views.create_request_quotation, name="create_request_quotation"),
    path('accepted_quotations_list/', views.accepted_quotations_list, name="accepted_quotations_list"),
    path('create_purchase_request_from_quotation/<int:quotation_id>/', views.create_purchase_request_from_quotation, name='create_purchase_request_from_quotation'),
    path('request_quotation_list/', views.request_quotation_list, name="request_quotation_list"),  
    path('request_quotation_detail/<int:quotation_id>/', views.request_quotation_detail, name="request_quotation_detail"),
    path('edit_unit_price_rq/<int:item_id>/', views.edit_unit_price_rq, name='edit_unit_price_rq'),
    path('view_supplier_quotations/<str:quotation_id>/', views.view_supplier_quotations, name="view_supplier_quotations"),
    path('supplier_quotation_submission_detail/<int:submission_id>/', views.supplier_quotation_submission_detail, name="supplier_quotation_submission_detail"),
    path('purchase_request_list/', views.purchase_request_list, name="purchase_request_list"),
    path('purchase_request_detail/<int:pr_id>', views.purchase_request_detail, name="purchase_request_detail"),
    path('purchase_invoice_list/', views.purchase_invoice_list, name="purchase_invoice_list"),
    path('purchase_invoice_detail/<int:pi_id>/', views.purchase_invoice_detail, name="purchase_invoice_detail"),
]
