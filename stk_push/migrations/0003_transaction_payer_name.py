# Generated by Django 5.0.6 on 2024-11-26 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stk_push', '0002_transaction_mpesa_receipt_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payer_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
