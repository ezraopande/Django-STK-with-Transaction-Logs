from django.contrib import admin

from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'phone_number', 'amount', 'status', 'date_created')
    list_filter = ('status', 'date_created')
    search_fields = ('transaction_id', 'phone_number')
