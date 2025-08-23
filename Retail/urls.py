from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from authu.views import dashboard_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/login/', lambda request: redirect('authu:login')),
    path('accounts/login/', lambda request: redirect('authu:login')),
    path('authu/', include('authu.urls')),
    path('', lambda request: redirect('dashboard')),  # root redirects to dashboard
    path('dashboard/', dashboard_view, name="dashboard"),

    # include Product app urls
    path('product/', include('Product.urls')),
    path('order/', include('Order.urls')),
    path('sales/', include('Sales.urls')),
    path('inventory/', include('Inventory.urls')),
    path('customer/', include('Customer.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
