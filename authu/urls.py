from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'authu'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    path('products/', views.product_management, name='product_management'),
    path('inventory/', views.inventory_management, name='inventory_management'),
    path('profile/', views.user_profile, name='user_profile'),
    path('settings/', views.settings_view, name='settings'),
]
