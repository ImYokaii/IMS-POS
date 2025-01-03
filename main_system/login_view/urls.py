from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.landing_page, name="landing_page"),
    path('login/', views.login_page, name="login"),
    path('employee_signup_page/', views.employee_signup_page, name="employee_signup_page"),
    path('supplier_signup_page/', views.supplier_signup_page, name="supplier_signup_page"),
    path('logout/', views.logout_page, name="logout"),
    path('wait_for_permission/', views.wait_for_permission, name="wait_for_permission"),
]