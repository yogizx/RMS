from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Product.models import Product
from Order.models import Order
from Sales.models import Sales
from django.utils.timezone import now
from decimal import Decimal
from django.db import models

@login_required
def dashboard_view(request):
    total_products = Product.objects.count()
    orders_today = Order.objects.all().count()   # remove date filter temporarily
    revenue_today = (
        Sales.objects.aggregate(total=models.Sum("total_amount"))["total"]
        or Decimal("0.00")
    )
    low_stock_count = Product.objects.filter(quantity__lt=10).count()

    print(">>> Products:", total_products)
    print(">>> Orders:", orders_today)
    print(">>> Revenue:", revenue_today)
    print(">>> Low stock:", low_stock_count)

    return render(request, "Retail/dashboard.html", {
        "total_products": total_products,
        "orders_today": orders_today,
        "revenue_today": revenue_today,
        "low_stock_count": low_stock_count,
    })
