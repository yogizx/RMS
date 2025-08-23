from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from Product.models import Product
from .models import StockHistory
from .forms import StockAdjustmentForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

@login_required
def dashboard(request):
    """Enhanced inventory dashboard with search and filtering"""
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'name')
    
    # Base queryset - show all products regardless of stock history
    products = Product.objects.all()
    
    # Search functionality
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(barcode_number__icontains=search_query)
        )
    
    # Sorting
    valid_sorts = {
        'name': 'name',
        'price': 'price',
        'quantity': 'quantity',
        'price_desc': '-price',
        'quantity_desc': '-quantity'
    }
    
    if sort_by in valid_sorts:
        products = products.order_by(valid_sorts[sort_by])
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Stock alerts
    low_stock_threshold = 5
    low_stock_products = products.filter(quantity__lt=low_stock_threshold)
    
    # Calculate total inventory value
    total_value = sum(float(product.price) * float(product.quantity) for product in products)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
        'low_stock_count': low_stock_products.count(),
        'total_value': total_value,
        'stock_adjustment_form': StockAdjustmentForm()
    }
    
    return render(request, "Inventory/dashboard.html", context)

@login_required
def stock_history(request):
    """Enhanced stock history with filtering"""
    search_query = request.GET.get('search', '')
    history = StockHistory.objects.select_related("product", "updated_by").order_by("-timestamp")
    
    if search_query:
        history = history.filter(
            Q(product__name__icontains=search_query) |
            Q(note__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(history, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query
    }
    
    return render(request, "Inventory/stock_history.html", context)

@login_required
def product_stock_detail(request, product_id):
    """Detailed view of a product's stock history"""
    product = get_object_or_404(Product, id=product_id)
    stock_history = StockHistory.objects.filter(product=product).order_by('-timestamp')
    
    context = {
        'product': product,
        'stock_history': stock_history
    }
    
    return render(request, "Inventory/current_stock.html", context)

def sync_inventory_view(request):
    """Manual sync endpoint for inventory - syncs all existing products"""
    from django.core.management import call_command
    
    try:
        call_command('sync_inventory')
        messages.success(request, "✅ Inventory synced successfully! All products are now in sync.")
    except Exception as e:
        messages.error(request, f"❌ Error syncing inventory: {e}")
    
    return redirect('Inventory:dashboard')