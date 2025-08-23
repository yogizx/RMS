# inventory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from Product.models import Product
from .utils import update_stock
from .models import StockHistory
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction

@login_required
@require_POST
def add_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        qty = int(request.POST.get('qty', 0))
        note = request.POST.get('note', '') or 'Restocked'
        if qty <= 0:
            raise ValueError("Quantity must be positive.")
        with transaction.atomic():
            update_stock(product, qty_change=qty, user=request.user, note=note)
        messages.success(request, f"Added {qty} to stock for {product.name}.")
    except Exception as e:
        messages.error(request, f"Could not add stock: {e}")
    return redirect('Product:product_list', pk=product.id)

@login_required
@require_POST
def sell_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        qty = int(request.POST.get('qty', 0))
        note = request.POST.get('note', '') or 'Sale'
        if qty <= 0:
            raise ValueError("Quantity must be positive.")
        with transaction.atomic():
            update_stock(product, qty_change=-qty, user=request.user, note=note)
        messages.success(request, f"Sold {qty} of {product.name}.")
    except Exception as e:
        messages.error(request, f"Could not sell: {e}")
    return redirect('Product:product_list', pk=product.id)

def current_stock(request):
    # quick proof it’s hit:
    print("🔥 current_stock view called")
    products = Product.objects.all()
    return render(request, "Inventory/current_stock.html", {"products": products})

def stock_history(request):
    history = StockHistory.objects.select_related("product", "updated_by").order_by("-timestamp")
    return render(request, "Inventory/stock_history.html", {"history": history})

@login_required
def sync_inventory_view(request):
    """Manual sync endpoint for inventory - syncs all existing products"""
    from django.core.management import call_command
    
    try:
        call_command('sync_inventory')
        messages.success(request, "✅ Inventory synced successfully! All products are now in sync.")
    except Exception as e:
        messages.error(request, f"❌ Error syncing inventory: {e}")
    
    return redirect('Inventory:dashboard')
