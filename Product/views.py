from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product
from .forms import ProductForm
from django.contrib import messages
import barcode
from barcode.writer import ImageWriter
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
import barcode
from barcode.writer import ImageWriter
from .forms import ProductForm
import os
import uuid
from django.core.files import File
from pathlib import Path

logger = logging.getLogger(__name__)

# ------------------------
# BARCODE GENERATION UTILS
# ------------------------

def product_home(request):
    return render(request, "Product/barcode_generate.html")

def generate_unique_barcode():
    """Generate a unique 12-digit barcode number that doesn't exist in DB."""
    while True:
        barcode_number = str(uuid.uuid4().int)[:12]
        if not Product.objects.filter(barcode_number=barcode_number).exists():
            return barcode_number

def save_barcode_image(barcode_number):
    """Generate and save barcode image into media/barcodes folder."""
    try:
        barcode_class = barcode.get_barcode_class('code128')
        writer = ImageWriter()
        options = {
            "module_width": 0.5,
            "module_height": 50.0,
            "font_size": 16,
            "dpi": 300,
            "text_distance": 2.0,
            "quiet_zone": 6.5,
            "background": "white",
            "foreground": "black",
            "write_text": True
        }
        barcode_img = barcode_class(barcode_number, writer=writer)
        barcode_dir = os.path.join(settings.MEDIA_ROOT, 'barcodes')
        os.makedirs(barcode_dir, exist_ok=True)
        filename_no_ext = os.path.join(barcode_dir, barcode_number)
        if os.path.exists(f"{filename_no_ext}.png"):
            os.remove(f"{filename_no_ext}.png")
        barcode_img.save(filename_no_ext, options)
        return f"barcodes/{barcode_number}.png"
    except Exception as e:
        logger.error(f"Failed to save barcode image: {e}")
        raise

# ------------------------
# VIEWS
# ------------------------
def generate_barcode(request):
    units = ['Gram', 'Kg', 'Liter', 'Piece']
    
    if request.method == 'POST':
        form = ProductForm(request.POST or None)
        product = None
        if form.is_valid():
            try:
                product = form.save(commit=False)

                # Auto-generate barcode if not manually provided
                generate_barcode_checked = request.POST.get('generate_barcode') == 'on'

                if generate_barcode_checked or not product.barcode_number:
                    barcode_number = generate_unique_barcode()
                    barcode_image_path = save_barcode_image(barcode_number)
                    product.barcode_number = barcode_number
                    product.barcode_image.name = barcode_image_path

                # Generate barcode image
                code = product.barcode_number
                Path('Product/media/barcode').mkdir(parents=True, exist_ok=True)
                barcode_path = f"Product/media/barcode/{code}"
                ean = barcode.get('ean13', code, writer=ImageWriter())
                ean.save(barcode_path)

                # Save image to model
                with open(f"{barcode_path}.png", "rb") as f:
                    product.barcode_image.save(f"{code}.png", File(f), save=False)

                product.save()
                messages.success(request, "✅ Product saved successfully!")
                return redirect('Product:product_list', product_id=product.id)

            except Exception as e:
                messages.error(request, f"❌ Error saving product: {e}")
        else:
            messages.error(request, "⚠ Please correct the errors in the form.")
    else:
        form = ProductForm()

    return render(request, 'Product/barcode_generate.html', {'form': form, 'units': units})

def barcode_success(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'Product/barcode_success.html', {'product': product})


def product_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'Product/product_list.html', {'products': products})


def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    units = ['Gram', 'Kg', 'Liter', 'Piece']  # for dropdown
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "✏ Product updated successfully.")
            return redirect('Product:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'Product/product_edit.html', {'form': form, 'product': product, 'units': units})


def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "🗑 Product deleted successfully.")
        return redirect('Product:product_list')

    return render(request, 'Product/product_delete_confirm.html', {'product': product})


# ------------------------
# Barcode Verification
# ------------------------
def barcode_verify(request):
    return render(request, 'Product/barcode_verify.html')


def verify_barcode_data(request):
    barcode_number = request.GET.get('barcode', '').strip()
    data = {'found': False}

    try:
        product = Product.objects.filter(barcode_number=barcode_number).first()
        if not product:
            # fallback: match ending digits
            product = Product.objects.filter(barcode_number__endswith=barcode_number).first()

        if product:
            # Generate barcode image if missing
            if not product.barcode_image and product.barcode_number:
                try:
                    barcode_image_path = save_barcode_image(product.barcode_number)
                    product.barcode_image.name = barcode_image_path
                    product.save()
                except Exception as e:
                    import logging
                    logging.error(f"Error generating barcode image: {e}")

            data = {
                'found': True,
                'name': product.name,
                'quantity': product.quantity,
                'unit': product.unit,
                'price': product.price,
                'description': product.description or 'No description',
                'barcode_image': product.barcode_image.url if product.barcode_image else ''
            }

    except Exception as e:
        import logging
        logging.error(f"Error verifying barcode: {e}")
        data['error'] = str(e)

    return JsonResponse(data)

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # handle form submission here
    return render(request, "Product/product_edit.html", {"product": product})

#8901491983228.