from django.contrib import admin

from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'phone_number', 'amount', 'status', 'mpesa_receipt_number', 'transaction_date')
    list_filter = ('status', 'date_created', 'transaction_date')
    search_fields = ('transaction_id', 'phone_number', 'mpesa_receipt_number')
