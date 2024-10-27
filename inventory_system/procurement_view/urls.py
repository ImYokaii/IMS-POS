from django.urls import path
from . import views

urlpatterns = [
    path('create_request_quotation/', views.create_request_quotation, name="create_request_quotation"),
    path('request_quotation_list/', views.request_quotation_list, name="request_quotation_list"),  
    path('request_quotation_detail/<int:quotation_id>/', views.request_quotation_detail, name="request_quotation_detail"),
]
