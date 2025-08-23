from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CustomerForm, PurchaseForm
from .models import Customer, Purchase
from django.contrib import messages

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        phone = request.POST.get("phone")

        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, "This phone number is already registered!")
            return redirect("Customer:add_customer")
        
        if form.is_valid():
            customer = form.save(commit=False)  # don't save to DB yet
            customer.user = request.user        # set the logged-in user
            customer.save()           
            messages.success(request, "Customer added successfully!")          # now save to DB
            return redirect('Customer:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer/add_customer.html', {'form': form})


#def customer_list(request):
    #customers = Customer.objects.all()
    #return render(request, 'customer/customer_list.html', {'customers': customers})
@login_required
def customer_list(request):
    customers = Customer.objects.prefetch_related('orders').all()
    return render(request, 'Customer/customer_list.html', {'customers': customers})

@login_required
def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('purchase_list')
    else:
        form = PurchaseForm()
    return render(request, 'Customer/add_purchase.html', {'form': form})


@login_required
#def purchase_list(request):
    #purchases = Purchase.objects.filter(customer__user=request.user)
    #return render(request, 'customer/purchase_list.html', {'purchases': purchases})
def purchase_list(request):
    purchases = Purchase.objects.all()
    return render(request, 'Customer/purchase_list.html', {'purchases': purchases})

def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    return redirect('Customer:customer_list')


def delete_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    purchase.delete()
    return redirect('purchase_list')
