# Generated by Django 5.0.7 on 2024-10-31 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_view', '0008_alter_product_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]