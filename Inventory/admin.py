from django.contrib import admin
from .models import StockHistory

@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'change_quantity', 'updated_by', 'timestamp', 'note')
    list_filter = ('updated_by', 'timestamp')
    search_fields = ('product__name', 'note')
