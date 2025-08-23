from django.db import transaction
from django.core.exceptions import ValidationError
from .models import StockHistory

def update_stock(product, qty_change, user=None, note=""):
    """
    Updates product.quantity and logs StockHistory.
    qty_change: +N to add, -N to remove
    Prevents negative stock.
    """
    with transaction.atomic():
        new_qty = product.quantity + qty_change
        if new_qty < 0:
            raise ValidationError(f"Insufficient stock: cannot reduce below 0 (current {product.quantity}).")
        product.quantity = new_qty
        product.save(update_fields=['quantity'])

        StockHistory.objects.create(
            product=product,
            change_quantity=qty_change,
            updated_by=user,
            note=note
        )
