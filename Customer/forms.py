from django import forms
from .models import Customer, Purchase

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone']


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['customer', 'product', 'quantity', 'price']