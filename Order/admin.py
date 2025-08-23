from django.contrib import admin
from .models import Order
# Order Admin
admin.site.register(Order)

# OrderItem Admin
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'amount', 'line_total']

    def line_total(self, obj):
        return obj.quantity * obj.amount  # or obj.unit_price * obj.quantity
    line_total.short_description = "Total"

