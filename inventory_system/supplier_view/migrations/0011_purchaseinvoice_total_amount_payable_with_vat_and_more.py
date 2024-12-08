# Generated by Django 5.0.7 on 2024-12-07 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_view', '0010_rename_invoice_purchaseinvoiceitem_purchase_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseinvoice',
            name='total_amount_payable_with_vat',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='purchaseinvoice',
            name='total_amount_payable',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]