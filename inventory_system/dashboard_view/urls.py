from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('product_levels/', views.product_levels, name="product_levels"),

]