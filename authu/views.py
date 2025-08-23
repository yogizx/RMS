from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import InventoryItem
from Product.models import Product
from Inventory.models import Product

@login_required
def dashboard_view(request):
    return render(request, "Retail/dashboard.html")

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        # Create user with password hashing
        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'authu/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    return render(request, 'authu/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    if not request.user.is_authenticated:
        return render(request, 'Retail/dashboard.html')
    
    products = Product.objects.all()
    return render(request, 'Retail/dashboard.html', {'products': products})


@login_required(login_url='login')
def home_view(request):
    return render(request, 'Retail/dashboard.html')
@login_required
def product_management(request):
    products = Product.objects.all()
    return render(request, 'Products/barcode_generate.html', {'products': products})

@login_required
def inventory_management(request):
    inventory = InventoryItem.objects.all()
    return render(request, 'Inventory/current_stock.html', {'inventory': inventory})

@login_required
def user_profile(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = request.user
        if email:
            user.email = email
        if password:
            user.set_password(password)  # password needs hashing
        user.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('user_profile')

    return render(request, 'authu/user_profile.html')

@login_required
def settings_view(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        company_email = request.POST.get('company_email')
        currency = request.POST.get('currency')
        timezone = request.POST.get('timezone')

        # You could save these into a model or Django's Site settings
        request.session['company_name'] = company_name
        request.session['company_email'] = company_email
        request.session['currency'] = currency
        request.session['timezone'] = timezone

        messages.success(request, "Settings updated successfully!")
        return redirect('settings')

    return render(request, 'authu/settings.html', {
        'company_name': request.session.get('company_name', ''),
        'company_email': request.session.get('company_email', ''),
        'currency': request.session.get('currency', 'USD'),
        'timezone': request.session.get('timezone', 'Asia/Kolkata'),
    })