# Generated by Django 5.0.7 on 2024-12-07 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_view', '0012_purchaseinvoiceitem_price_valid_until'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseinvoiceitem',
            name='price_valid_until',
        ),
        migrations.AddField(
            model_name='quotationsubmissionitem',
            name='price_valid_until',
            field=models.DateField(blank=True, null=True),
        ),
    ]
