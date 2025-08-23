from django.db import models
from django.contrib.auth.models import User
from Product.models import Product

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="purchases")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True) # dropdown
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Update stock automatically
        if not self.pk:
            self.product.quantity += self.quantity
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - {self.customer.name}"

    @property
    def total_amount(self):
        return self.quantity * self.price
