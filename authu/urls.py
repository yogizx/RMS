from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'authu'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('products/', views.product_management, name='product_management'),
    path('inventory/', views.inventory_management, name='inventory_management'),
    path('profile/', views.user_profile, name='user_profile'),
    path('settings/', views.settings_view, name='settings'),
    path("login/", auth_views.LoginView.as_view(template_name="authu/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
