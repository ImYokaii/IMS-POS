# Generated by Django 5.0.7 on 2024-10-31 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_view', '0013_remove_product_barcode_remove_product_supplier_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Wasted', 'Wasted')], default=('Active', 'Active'), max_length=50),
        ),
    ]
