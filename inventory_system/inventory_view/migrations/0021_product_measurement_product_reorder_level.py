# Generated by Django 5.0.7 on 2024-11-23 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_view', '0020_alter_product_status_alter_wasteproduct_date_wasted'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='measurement',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='reorder_level',
            field=models.PositiveIntegerField(default=1, null=True),
        ),
    ]