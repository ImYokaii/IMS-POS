# Generated by Django 5.0.7 on 2024-10-31 08:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_view', '0012_alter_product_supplier_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='barcode',
        ),
        migrations.RemoveField(
            model_name='product',
            name='supplier_name',
        ),
    ]