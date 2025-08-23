from django.urls import path
from . import views

app_name = 'Sales'

urlpatterns = [
    path('', views.base_view, name='base'),
    path('daily/', views.daily_view, name='daily'),
    path('monthly/', views.monthly_view, name='monthly'),
    path('products/', views.products_view, name='products'),
    path('top-sellers/', views.top_sellers_view, name='top_sellers'),
    path('customers/', views.customers_view, name='customers'),

    # APIs & exports
    path('api/transactions/', views.api_recent_transactions, name='api_transactions'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/json/', views.export_json, name='export_json'),
]