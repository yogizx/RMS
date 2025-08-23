# inventory/models.py
from django.db import models
from django.contrib.auth.models import User
from Product.models import Product  

class StockHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    change_quantity = models.IntegerField()  # + for added stock, - for removed
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"{self.product.name} - {self.change_quantity} at {self.timestamp}"
