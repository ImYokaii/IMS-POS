from django.urls import path
from . import views

urlpatterns = [
    path('pos_page/', views.pos_page, name='pos_page'),
    path('pos_page/add_item/', views.add_item, name='add_item'),
    path('pos_page/edit_item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('pos_page/delete_item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('pos_page/complete_invoice/', views.complete_invoice, name='complete_invoice'),
    path('pos_page/input_cash/<int:invoice_id>/', views.input_cash, name='input_cash'),
    path('pos_page/transaction_summary/<int:invoice_id>/', views.transaction_summary, name='transaction_summary'),
    path('pos_page/finish_transaction/<int:invoice_id>/', views.finish_transaction, name='finish_transaction'),
     path('pos_page/transaction_invoices/', views.transaction_invoices, name='transaction_invoices'),
]

