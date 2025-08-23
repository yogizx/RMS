from django.urls import path
from . import views

app_name = 'Order'

urlpatterns = [
    
    # ------------------------
    # ORDER / BILLING
    # ------------------------
    path("order/", views.order, name="order"),
    path("order_create/", views.order_create, name="order_create"),
    path("checkout/", views.checkout, name="checkout"),
    path("add_to_order/", views.add_to_order, name="add_to_order"),  # ✅ trailing slash
    path("clear_order/", views.clear_order, name="clear_order"),
    path("update_quantity/", views.update_quantity, name="update_quantity"),
    path("generate_invoice_pdf/", views.generate_invoice_pdf, name="generate_invoice_pdf"),
    path("test_pdf/", views.test_pdf, name="test_pdf"),
    path("save_order/", views.save_order, name="save_order"),
]