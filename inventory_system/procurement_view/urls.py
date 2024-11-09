from django.urls import path
from . import views

urlpatterns = [
    path('create_request_quotation/', views.create_request_quotation, name="create_request_quotation"),
    path('create_purchase_request/', views.create_purchase_request, name="create_purchase_request"),
    path('request_quotation_list/', views.request_quotation_list, name="request_quotation_list"),  
    path('request_quotation_detail/<int:quotation_id>/', views.request_quotation_detail, name="request_quotation_detail"),
    path('view_supplier_quotations/<str:quotation_no>/', views.view_supplier_quotations, name="view_supplier_quotations"),
    path('quotation_submission_detail/<int:submission_id>/', views.view_quotation_submission_detail, name="quotation_submission_detail"),
    path('purchase_invoice_list/', views.purchase_invoice_list, name="purchase_invoice_list"), 
    path('purchase_invoice_detail/<int:pi_id>/', views.purchase_invoice_detail, name="purchase_invoice_detail"),
]
