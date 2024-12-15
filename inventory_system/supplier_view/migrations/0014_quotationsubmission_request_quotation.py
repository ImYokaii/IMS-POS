# Generated by Django 5.0.7 on 2024-12-10 07:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement_view', '0027_alter_purchaseorder_delivery_date'),
        ('supplier_view', '0013_remove_purchaseinvoiceitem_price_valid_until_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotationsubmission',
            name='request_quotation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quotation_submissions', to='procurement_view.requestquotation'),
        ),
    ]