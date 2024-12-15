# Generated by Django 5.0.7 on 2024-12-10 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement_view', '0027_alter_purchaseorder_delivery_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestquotationitem',
            name='price_valid_until',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='requestquotationitem',
            name='product_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='requestquotationitem',
            name='quantity',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='requestquotationitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]