from django.urls import path
from . import views


urlpatterns = [
    path('request_quotations_list/', views.request_quotations_list, name="request_quotations_list"),
    path('request_quotations_detail/<int:quotation_id>', views.request_quotations_detail, name="request_quotations_detail"),
    path('create_quotation_submission/', views.create_quotation_submission, name="create_quotation_submission"),
]