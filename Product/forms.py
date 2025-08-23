from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Updated fields to match the current Product model
        fields = ['name', 'price', 'quantity', 'unit', 'barcode_number', 'barcode_image', 'description']
        widgets = {
            'barcode_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'barcode_image': forms.FileInput(attrs={'disabled': True}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional product description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make barcode fields optional in the form
        self.fields['barcode_image'].required = False
        self.fields['barcode_number'].required = False
        # Optional: placeholder for name and price fields
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter product name'})
        self.fields['price'].widget.attrs.update({'placeholder': 'Enter price'})
        self.fields['quantity'].widget.attrs.update({'placeholder': 'Enter quantity'})
