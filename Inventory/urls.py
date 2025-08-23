from django.urls import path
from django.http import HttpResponse
from . import views, views_enhanced
from .views_enhanced import dashboard, stock_history, product_stock_detail

app_name = 'Inventory' 

urlpatterns = [
    # Dashboard - main inventory page
    path('', dashboard, name='dashboard'),
    path('dashboards/', dashboard, name='dashboards'),
    
    # Stock management
    path('current-stock/', views.current_stock, name='current_stock'),
    path('stock-history/', stock_history, name='stock_history'),
    path('product-stock/<int:product_id>/', product_stock_detail, name='product_stock_detail'),
    
    # Stock adjustment endpoints
    path('add-stock/<int:product_id>/', views.add_stock, name='add_stock'),
    path('sell-product/<int:product_id>/', views.sell_product, name='sell_product'),
    
    # Sync inventory endpoint
    path('sync/', views_enhanced.sync_inventory_view, name='sync_Inventory'),
    
    # Legacy routes
    path('ping/', lambda r: HttpResponse('pong from inventory')),
]
