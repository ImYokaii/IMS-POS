from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('product_list/', views.product_list, name="product_list"),
    path('product_list/product_view/<int:product_id>/', views.product_view, name="product_view"),

    path('restock_product_list/', views.restock_product_list, name="restock_product_list"),
    path('restock_product_list/restock_product_quantity/<int:product_id>/', views.restock_product_quantity, name="restock_product_quantity"),
    
    path('to_waste_product_list/', views.to_waste_product_list, name="to_waste_product_list"),
    path('to_waste_product_list/transfer_to_waste/<int:product_id>/', views.transfer_to_waste, name="transfer_to_waste"),

    path('edit_product_list/', views.edit_product_list, name="edit_product_list"),
    path('edit_product_list/edit_product/<int:product_id>/', views.edit_product, name="edit_product"),

    path('add_new_product/', views.add_new_product, name="add_new_product"),
    path('wasted_product_list/', views.wasted_product_list, name="wasted_product_list"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)