from datetime import datetime, timedelta
from django.db.models import Sum, Count, F
from django.utils import timezone
from .models import Order, OrderItem, Product, Category, Customer
from decimal import Decimal

def daterange_qs(qs, start, end):
    if start:
        qs = qs.filter(created_at__date__gte=start)
    if end:
        qs = qs.filter(created_at__date__lte=end)
    return qs

def revenue_for_date(dt):
    start = datetime(dt.year, dt.month, dt.day, 0, 0, 0, tzinfo=timezone.get_current_timezone())
    end = start + timedelta(days=1)
    return OrderItem.objects.filter(order__created_at__gte=start, order__created_at__lt=end).aggregate(
        revenue=Sum(F('unit_price') * F('quantity'))
    )['revenue'] or 0

def percent_change(today, yesterday):
    if yesterday == 0:
        return 0 if today == 0 else 100
    return round(((today - yesterday) / yesterday) * 100, 2)
