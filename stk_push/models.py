from django.db import models


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, blank=True, null=True) 
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True) 
    status = models.CharField(max_length=50, blank=True, null=True)  
    description = models.TextField(blank=True, null=True)  
    transaction_date = models.DateTimeField(blank=True, null=True)  
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.mpesa_receipt_number or self.transaction_id} - {self.status}"

