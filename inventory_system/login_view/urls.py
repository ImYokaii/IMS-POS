from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('signup/', views.signup_page, name="signup"),
    path('logout/', views.logout_page, name="logout"),
    path('managers/', views.manager_page, name="managers"),
    path('employees/', views.employee_page, name="employees"),
    path('suppliers/', views.supplier_page, name="suppliers"),
    path('unknown/', views.unknown_page, name="unknowns"),
]