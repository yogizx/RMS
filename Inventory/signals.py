from django.db.models.signals import post_save
from django.dispatch import receiver
from Product.models import Product
from .models import StockHistory

@receiver(post_save, sender=Product)
def sync_product_to_inventory(sender, instance, created, **kwargs):
    """
    Automatically sync new products to inventory by creating initial stock history.
    When a new product is created, create an initial stock entry with the initial quantity.
    """
    if created:
        # Create initial stock history entry for the new product
        StockHistory.objects.create(
            product=instance,
            change_quantity=instance.quantity,
            updated_by=None,  # System created
            note=f"Initial stock sync - Product added with {instance.quantity} units"
        )
