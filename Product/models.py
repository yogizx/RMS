from django.db import models

class Product(models.Model):
    UNIT_CHOICES = [
        ('Gram', 'Gram'),
        ('Kg', 'Kg'),
        ('Liter', 'Liter'),
        ('Piece', 'Piece'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.FloatField()
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='Piece')
    barcode_number = models.CharField(max_length=50, unique=True, default="000000", null=True)
    barcode_image = models.ImageField(upload_to='barcode/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)  # optional description

    def __str__(self):
        return f"{self.name} ({self.barcode_number})"

    def get_barcode(self):
        """
        Returns the barcode number as a string with all leading/trailing spaces removed.
        Useful for live scanning matching.
        """
        return str(self.barcode_number).strip()
