from django.urls import path
from django.conf.urls.static import static
from . import views
from .views import scan_qr_code

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('product_levels/', views.product_levels, name="product_levels"),
    path('product_levels/edit_reorder_levels/<int:product_id>/', views.edit_reorder_levels, name="edit_reorder_levels"),
    path('low_stock_products/', views.low_stock_products, name="low_stock_products"),
    path('scan/', scan_qr_code, name='scan_qr_code'),
    
]