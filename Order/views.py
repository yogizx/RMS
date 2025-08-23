from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import io
import base64
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import qrcode
from Product.models import Product
import json
from decimal import Decimal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm
from . models import Invoice
from datetime import datetime
from .models import Order
from Customer.models import Customer

# ------------------------
# ORDER / BILLING
# ------------------------
def order_create(request):
    # Show billing page with scanner
    order_items = request.session.get("order_items", [])
    total = sum(Decimal(item["price"]) * item["quantity"] for item in order_items)
    return render(request, "Order/order_create.html", {"order_items": order_items, "total": total})

def checkout(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "")
        customer_phone = request.POST.get("customer_phone", "")
        payment_method = request.POST.get("payment_method")

        # Example: Fetch cart/order items
        order_items = request.session.get("cart", [])
        total = sum(item["price"] * item["quantity"] for item in order_items)

        # 🔹 Create invoice record
        invoice = Invoice.objects.create()
        invoice_number = invoice.invoice_number  # e.g. INV-0007

        # Generate QR if payment = UPI
        qr_code = None
        if payment_method == "upi":
            upi_id = "merchant@upi"  # Replace with your UPI ID
            upi_link = f"upi://pay?pa={upi_id}&am={total}&cu=INR"
            qr = qrcode.make(upi_link)
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")
            qr_code = base64.b64encode(buffer.getvalue()).decode()

        return render(request, "Order/invoice.html", {
            "order_items": order_items,
            "total": total,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "payment_method": payment_method,
            "qr_code": qr_code,
        })

    return render(request, "Order/checkout.html")

def add_to_order(request):
    barcode = request.GET.get("barcode")
    try:
        product = Product.objects.get(barcode_number=barcode)
        cart = request.session.get("cart", {})

        product_id = str(product.id)

        # If product not in cart, add it with quantity = product.quantity from DB
        if product_id not in cart:
            cart[product_id] = {
                "name": product.name,
                "price": float(product.price),
                "quantity": product.quantity  # use DB quantity
            }

        request.session["cart"] = cart

        return JsonResponse({
            "success": True,
            "item": {
                "barcode": product.barcode_number,  # important!
                "product_name": product.name,
                "product_price": float(product.price),
                "quantity": product.quantity
            }
        })

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Product not found"})

def order(request):
    return render(request, "order.html", {"items": []})

def clear_order(request):
    request.session["cart"] = {}
    return JsonResponse({"success": True})

def update_quantity(request):
    product_id = request.GET.get("product_id")
    quantity = int(request.GET.get("quantity", 1))
    cart = request.session.get("cart", {})
    if product_id in cart:
        cart[product_id]["quantity"] = quantity
        request.session["cart"] = cart
    return JsonResponse({"success": True})

def remove_item(request):
    barcode = request.GET.get("barcode")
    cart = request.session.get("cart", {})
    if barcode in cart:
        del cart[barcode]
        request.session["cart"] = cart
    return JsonResponse({"success": True})

@csrf_exempt  # temporary to test PDF generation
def generate_invoice_pdf(request):
    if request.method == "POST":
        # Get form data
        name = request.POST.get("customer_name", "N/A")
        phone = request.POST.get("customer_phone", "N/A")
        payment = request.POST.get("payment_type", "N/A")
        date = request.POST.get("date")
        items = json.loads(request.POST.get("items", "[]"))

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)  # <-- instance
        c.setFont("Helvetica", 10)               # <-- call on instance
        c.drawString(50, 50, "Hello Footer")
        c.showPage()
        c.save()
        buffer.seek(0)
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        # --- Shop Info ---
        shop_name = Paragraph("<b>My Shop Name</b>", styles['Title'])
        shop_contact = Paragraph("Address: 123, Main Street, City<br/>Phone: +91 9876543210<br/>Email: shop@example.com", styles['Normal'])
        elements.extend([shop_name, shop_contact, Spacer(1, 12)])

        # --- Invoice Number ---
        # Generate new invoice record
        invoice = Invoice()  # don’t call create()
        invoice.save()
        invoice_number = invoice.invoice_number
        invoice_para = Paragraph(f"<b>Invoice No:</b> {invoice_number}", styles['Normal'])
        elements.extend([invoice_para, Spacer(1, 12)])

        # --- Customer Info ---
        customer_info = Paragraph(f"<b>Customer:</b> {name} &nbsp;&nbsp; <b>Phone:</b> {phone} &nbsp;&nbsp; <b>Date:</b> {date} &nbsp;&nbsp; <b>Payment:</b> {payment}", styles['Normal'])
        elements.extend([customer_info, Spacer(1, 12)])

        items_json = request.POST.get("items", "[]")
        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            return HttpResponse("Invalid items JSON")  # convert JSON string to list of dicts

        # --- Table Header ---
        #["Product", "Qty", "Price (₹)", "Amount (₹)"]
        data = []
        total = 0
        for item in items:
            product_name = item.get("product_name") or item.get("name") or "Unknown"
            quantity = item.get("quantity", 0)
            price = item.get("product_price") or item.get("price") or 0
            amount = quantity * price
            total += amount
            data.append([product_name, str(quantity), f"{price:.2f}", f"{amount:.2f}"])

        # Grand Total row
        grand_total_label = Paragraph("<b>Grand Total</b>", styles['Normal'])
        grand_total_amount = Paragraph(f"<b>{total:.2f}</b>", styles['Normal'])

        # Then add it to the table
        data.append(["", "", grand_total_label, grand_total_amount])

        # Create Table
        table = Table(data, colWidths=[200, 50, 70, 70])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#007bff')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN',(1,1),(-1,-1),'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # --- UPI QR if needed ---
        if payment == "upi":
            upi_link = f"upi://pay?pa=merchant@upi&am={total}&tn=Order Payment"
            qr = qrcode.make(upi_link)
            qr_buffer = io.BytesIO()
            qr.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            rl_qr = RLImage(qr_buffer, width=50*mm, height=50*mm)
            elements.append(Paragraph("<b>Scan to Pay via UPI:</b>", styles['Normal']))
            elements.append(rl_qr)

        # After drawing all your items and totals
        footer_text = "📍 My Shop Name | 📞 +91-1234567890 | Thank you for your purchase!"
        c.setFont("Helvetica", 10)
        c.drawCentredString(A4[0] / 2, 20, footer_text)  # y=20 from bottom

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="Invoice.pdf")
        

def test_pdf(request):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Hello PDF")
    c.showPage()
    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='test.pdf')

@csrf_exempt
def save_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            items = data.get("items", [])
            customer_name = data.get("customer_name") or "Guest"
            customer_phone = data.get("customer_phone") or "N/A"

            customer, _ = Customer.objects.get_or_create(
                name=customer_name,
                phone=customer_phone
            )

            # Generate invoice number
            from .models import Invoice
            invoice = Invoice.objects.create()
            invoice_number = invoice.invoice_number

            for item in items:
                barcode = item.get("barcode")
                if not barcode:
                    return JsonResponse({"success": False, "error": "Barcode missing"})

                try:
                    product = Product.objects.get(barcode_number=barcode)
                    quantity = item.get("quantity", 1)
                    price = item.get("price", 0)

                    Order.objects.create(
                        customer=customer,
                        customer_phone=customer_phone,  # store phone
                        product=product,
                        quantity=quantity,
                        total_amount=price * quantity,
                        invoice_number=invoice_number  # store invoice number
                    )
                except Product.DoesNotExist:
                    return JsonResponse({"success": False, "error": f"Product with barcode {barcode} not found"})

            return JsonResponse({"success": True, "invoice_number": invoice_number})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
