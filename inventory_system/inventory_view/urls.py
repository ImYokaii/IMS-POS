from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('product_list/', views.product_list, name="product_list"),
    path('product_list/product_view/<int:product_id>/', views.product_view, name="product_view"),
    path('add_item_choice/', views.add_item_choice, name="add_item_choice"),

    path('existing_product_page/', views.existing_product_page, name="existing_product_page"),
    path('existing_product_page/add_existing_product/<int:product_id>/', views.add_existing_product, name="add_existing_product"),
    
    path('add_item_choice/add_product_type/', views.add_product_type, name="add_product_type"),
    path('add_item_choice/add_product_type/add_perishale', views.add_perishable, name="add_perishable"),

    path('add_item_choice/add_product_type/add_nonperishale', views.add_nonperishable, name="add_nonperishable"),
    path('add_product_waste', views.add_product_waste, name="add_product_waste"),
    path('add_to_waste/<int:product_id>/', views.add_to_waste, name="add_to_waste"),
    path('wasted_product_list/', views.wasted_product_list, name="wasted_product_list"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)