from datetime import datetime, timedelta, date
from collections import defaultdict
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q, Max
from django.utils import timezone
from django.db.models.functions import TruncHour, TruncMonth
import csv
import json
from .models import Category, Product, Customer, Order, OrderItem
from .forms import DateRangeForm
from .utils import daterange_qs, revenue_for_date, percent_change


def base_view(request):
    return render(request, "Sales/base.html")

def _date_range_from_request(request):
    start = request.GET.get('start_date') or None
    end = request.GET.get('end_date') or None
    return (start, end)

def _kpis():
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    rev_today = revenue_for_date(today)
    rev_yday = revenue_for_date(yesterday)
    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_yday = Order.objects.filter(created_at__date=yesterday).count()

    active_customers_today = Customer.objects.filter(orders__created_at__date=today).distinct().count()
    active_customers_yday = Customer.objects.filter(orders__created_at__date=yesterday).distinct().count()

    growth_today = rev_today
    growth_yday = rev_yday

    return { 
        'revenue': {'value': rev_today, 'diff': percent_change(rev_today, rev_yday)},
        'orders': {'value': orders_today, 'diff': percent_change(orders_today, orders_yday)},
        'customers': {'value': active_customers_today, 'diff': percent_change(active_customers_today, active_customers_yday)},
        'growth': {'value': growth_today, 'diff': percent_change(growth_today, growth_yday)},
    }

def dashboard(request):
    form = DateRangeForm(request.GET or None)
    context = {
        'form': form,
        'kpis': _kpis(),
        'section': 'dashboard'
    }
    return render(request, 'Sales/base.html', context)

def daily_view(request):
    form = DateRangeForm(request.GET or None)
    start, end = _date_range_from_request(request)
    tz = timezone.get_current_timezone()
    qs = OrderItem.objects.select_related('order').all()
    if start:
        qs = qs.filter(order__created_at__date__gte=start)
    if end:
        qs = qs.filter(order__created_at__date__lte=end)

    hourly = qs.annotate(h=TruncHour('order__created_at')).values('h').annotate(
        revenue=Sum(F('unit_price') * F('quantity')),
        orders=Count('order', distinct=True)
    ).order_by('h')

    hours = [h['h'].astimezone(tz).strftime('%H:%M') for h in hourly]
    revenue = [float(h['revenue'] or 0) for h in hourly]

    recent = Order.objects.order_by('-created_at')[:10]
    transactions = [{
        'id': o.id,
        'customer': o.customer.name,
        'amount': float(sum(i.unit_price * i.quantity for i in o.items.all())),
        'created_at': o.created_at.astimezone(tz).strftime('%Y-%m-%d %H:%M')
    } for o in recent]

    context = { 
        'form': form,
        'kpis': _kpis(),
        'hours': hours,
        'revenue': revenue,
        'transactions': transactions,
        'section': 'daily',
    }
    return render(request, 'Sales/daily.html', context)

def monthly_view(request):
    form = DateRangeForm(request.GET or None)
    tz = timezone.get_current_timezone()

    month_rev = OrderItem.objects.annotate(m=TruncMonth('order__created_at')).values('m').annotate(
        revenue=Sum(F('unit_price') * F('quantity'))
    ).order_by('m')

    months = [m['m'].astimezone(tz).strftime('%b %Y') for m in month_rev]
    revs = [float(m['revenue'] or 0) for m in month_rev]

    by_cat = OrderItem.objects.values('product__category__name').annotate(
        revenue=Sum(F('unit_price') * F('quantity'))
    ).order_by('-revenue')

    cat_labels = [c['product__category__name'] for c in by_cat]
    cat_data = [float(c['revenue'] or 0) for c in by_cat]

    # Key performance metrics comparing this month vs last month
    today = timezone.localdate()
    first_of_month = today.replace(day=1)
    last_month_end = first_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    this_month_rev = OrderItem.objects.filter(order__created_at__date__gte=first_of_month).aggregate(
        r=Sum(F('unit_price') * F('quantity'))
    )['r'] or 0

    last_month_rev = OrderItem.objects.filter(order__created_at__date__gte=last_month_start, order__created_at__date__lte=last_month_end).aggregate(
        r=Sum(F('unit_price') * F('quantity'))
    )['r'] or 0

    perf = { 'this_month': float(this_month_rev), 'last_month': float(last_month_rev), 'diff': percent_change(float(this_month_rev), float(last_month_rev)) }

    context = {
        'form': form,
        'kpis': _kpis(),
        'months': months,
        'revs': revs,
        'cat_labels': cat_labels,
        'cat_data': cat_data,
        'perf': perf,
        'section': 'monthly',
    }
    return render(request, 'Sales/monthly.html', context)

def products_view(request):
    form = DateRangeForm(request.GET or None)

    top_products = OrderItem.objects.values('product__id','product__name','product__rating').annotate(
        units=Sum('quantity'),
        revenue=Sum(F('unit_price') * F('quantity'))
    ).order_by('-revenue')[:10]

    categories = Category.objects.values('id','name').annotate(
        product_count=Count('products'),
        revenue=Sum(F('products__orderitem__unit_price') * F('products__orderitem__quantity')),
    ).order_by('-revenue')

    context = {
        'form': form,
        'kpis': _kpis(),
        'top_products': top_products,
        'categories': categories,
        'section': 'products',
    }
    return render(request, 'Sales/products.html', context)

def top_sellers_view(request):
    form = DateRangeForm(request.GET or None)

    best_sellers = OrderItem.objects.values('product__id','product__name','product__rating','product__category__name').annotate(
        revenue=Sum(F('unit_price') * F('quantity')),
        units=Sum('quantity')
    ).order_by('-units')[:15]

    context = {
        'form': form,
        'kpis': _kpis(),
        'best_sellers': best_sellers,
        'section': 'top_sellers',
    }
    return render(request, 'Sales/top_sellers.html', context)

def customers_view(request):
    form = DateRangeForm(request.GET or None)

    top_customers = (
    Order.objects
    .values('customer__id', 'customer__name', 'customer__joined_at')
    .annotate(
        orders=Count('id'),
        spent=Sum(F('items__unit_price') * F('items__quantity')),
        last_purchase=Max('created_at')   # ✅ FIXED
    )
    .order_by('-spent')[:20]
)

    # Compute activity buckets (simple heuristic)
    today = timezone.localdate()
    activity = {
        'new_customers': Customer.objects.filter(joined_at__gte=today - timedelta(days=7)).count(),
        'regular_purchases': Customer.objects.filter(orders__created_at__gte=today - timedelta(days=30)).distinct().count(),
        'inactive_90d': Customer.objects.exclude(orders__created_at__gte=today - timedelta(days=90)).count()
    }

    context = {
        'form': form,
        'kpis': _kpis(),
        'top_customers': top_customers,
        'activity': activity,
        'section': 'customers',
    }
    return render(request, 'Sales/customers.html', context)

def api_recent_transactions(request):
    tz = timezone.get_current_timezone()
    recent = Order.objects.order_by('-created_at')[:10]
    data = [{
        'id': o.id,
        'customer': o.customer.name,
        'amount': float(sum(i.unit_price * i.quantity for i in o.items.all())),
        'created_at': o.created_at.astimezone(tz).strftime('%Y-%m-%d %H:%M')
    } for o in recent]
    return JsonResponse({'transactions': data})

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['order_id','customer','created_at','product','quantity','unit_price','total'])
    for it in OrderItem.objects.select_related('order','product','order__customer').all():
        writer.writerow([
            it.order_id,
            it.order.customer.name,
            it.order.created_at.strftime('%Y-%m-%d %H:%M'),
            it.product.name,
            it.quantity,
            float(it.unit_price),
            float(it.total_price)
        ])
    return response

def export_json(request):
    data = []
    for it in OrderItem.objects.select_related('order','product','order__customer').all():
        data.append({
            'order_id': it.order_id,
            'customer': it.order.customer.name,
            'created_at': it.order.created_at.isoformat(),
            'product': it.product.name,
            'quantity': it.quantity,
            'unit_price': float(it.unit_price),
            'total': float(it.total_price)
        })
    return HttpResponse(json.dumps(data, indent=2), content_type='application/json')
