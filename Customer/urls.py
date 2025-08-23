from django.urls import path
from . import views

app_name = 'Customer'

urlpatterns = [
    path('add/', views.add_customer, name='add_customer'),
    path('list/', views.customer_list, name='customer_list'),
    path('purchase/add/', views.add_purchase, name='add_purchase'),
    path('purchase/list/', views.purchase_list, name='purchase_list'),
    path('delete/<int:id>/', views.delete_customer, name='delete_customer'),
    path('purchase/delete/<int:purchase_id>/', views.delete_purchase, name='delete_purchase'),
]
