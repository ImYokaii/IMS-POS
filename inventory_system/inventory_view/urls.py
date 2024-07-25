from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.dummy_page, name=""),
    path('product_list/', views.product_list, name="product_list"),
    path('add_item_choice/', views.add_item_choice, name="add_item_choice"),
    path('existing_product_page/', views.existing_product_page, name="existing_product_page"),
    path('existing_product_page/add_existing_product/<int:product_id>/', views.add_existing_product, name="add_existing_product"),
    path('add_item_choice/add_product_type/', views.add_product_type, name="add_product_type"),
    path('add_item_choice/add_product_type/add_perishale', views.add_perishable, name="add_perishable"),
    path('add_item_choice/add_product_type/add_nonperishale', views.add_nonperishable, name="add_nonperishable"),
    path('filter_product_list', views.filter_product_list, name="filter_product_list"),
    path('add_to_waste/<int:product_id>/', views.add_to_waste, name="add_to_waste"),
    path('wasted_product_list/', views.wasted_product_list, name="wasted_product_list"),
]