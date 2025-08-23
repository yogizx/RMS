from django.db import models
from django.utils import timezone
from Customer.models import Customer
from Product.models import Product

# ------------------------
# ORDERS
# ------------------------
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.FloatField()
    date = models.DateField(auto_now_add=True)
    payment_type = models.CharField(max_length=20, default="cash")
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer} - {self.product}"

    def __str__(self):
        return f"Order {self.id} - {self.created_at}"
    
    def __str__(self):
        return f"{self.product.name} - {self.invoice_number or 'No Invoice'}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("Product.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price
    
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Example: use ID + timestamp or sequential number
            last_invoice = Invoice.objects.order_by('-id').first()
            next_id = (last_invoice.id + 1) if last_invoice else 1
            self.invoice_number = f"INV-{next_id:04d}"
        super().save(*args, **kwargs)
