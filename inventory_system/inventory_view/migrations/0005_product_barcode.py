# Generated by Django 5.0.7 on 2024-09-14 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_view', '0004_rename_reason_for_waste_wasteproduct_supplier_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='barcode',
            field=models.ImageField(default='barcodes/placeholder.jpg', upload_to='images/'),
        ),
    ]