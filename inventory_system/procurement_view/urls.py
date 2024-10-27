from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('create_request_quotation/', views.create_request_quotation, name="create_request_quotation"),
    path('invoice_generation/', views.invoice_generation, name="invoice_generation"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)