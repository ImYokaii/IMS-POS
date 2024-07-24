from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.dummy_page, name=""),
    path('product_list/', views.product_list, name="product_list"),
    path('add_stock_choice/', views.add_stock_choice, name="add_stock_choice"),
    path('add_perishale', views.add_perishable, name="add_perishable"),
    path('add_nonperishale', views.add_nonperishable, name="add_nonperishable"),
    path('filter_product_list', views.filter_product_list, name="filter_product_list"),
    path('add_to_waste/<int:product_id>/', views.add_to_waste, name="add_to_waste"),
    path('wasted_product_list/', views.wasted_product_list, name="wasted_product_list"),
]