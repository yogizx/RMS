from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'Product'

urlpatterns = [
    # Home page & Barcode generation
    path('', views.product_home, name='product_home'),
    path('generate/', views.generate_barcode, name='generate_barcode'),
    path('barcode/generate/', views.generate_barcode, name='barcode_generate'),
    # Product list page
    path('products/', views.product_list, name='product_list'),

    # Barcode generation success page
    path('success/<int:product_id>/', views.barcode_success, name='barcode_success'),

    # Edit & Delete product routes
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # Barcode verification (webcam / upload)
    path('verify/', views.barcode_verify, name='barcode_verify'),
    path('verify_barcode_data/', views.verify_barcode_data, name='verify_barcode_data'),  # API endpoint

    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)