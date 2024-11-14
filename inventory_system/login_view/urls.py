from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.landing_page, name="landing_page"),
    path('login/', views.login_page, name="login"),
    path('signup/', views.signup_page, name="signup"),
    path('logout/', views.logout_page, name="logout"),
    path('wait_for_permission/', views.wait_for_permission, name="wait_for_permission"),
]