from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('low_stock_products/', views.low_stock_products, name="low_stock_products"),
    path('financial_dashboard/', views.financial_dashboard, name="financial_dashboard"),
]