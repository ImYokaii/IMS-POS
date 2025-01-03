from django.urls import path
from . import views

urlpatterns = [
    path('pos_page/', views.pos_page, name='pos_page'),
    
    path('add_item/', views.add_item, name='add_item'),
    path('edit_item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),

    path('complete_invoice/', views.complete_invoice, name='complete_invoice'),
    path('input_cash/<int:invoice_id>/', views.input_cash, name='input_cash'),
    path('transaction_summary/<int:invoice_id>/', views.transaction_summary, name='transaction_summary'),
    path('finish_transaction/<int:invoice_id>/', views.finish_transaction, name='finish_transaction'),

    path('receipt_page/<int:invoice_id>/', views.receipt_page, name='receipt_page'),

    path('transaction_invoices/', views.transaction_invoices, name='transaction_invoices'),
    path('transaction_invoices_detail/<int:invoice_id>/', views.transaction_invoices_detail, name='transaction_invoices_detail'),

    path('download_sales_invoice_pdf/<int:invoice_id>/', views.download_sales_invoice_pdf, name='download_sales_invoice_pdf'),
]