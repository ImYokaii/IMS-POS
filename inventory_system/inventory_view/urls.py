from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.dummy_page, name=""),
    path('product_list/', views.product_list, name="product_list"),
]