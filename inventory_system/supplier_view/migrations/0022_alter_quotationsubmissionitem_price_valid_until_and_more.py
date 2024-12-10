# Generated by Django 5.0.7 on 2024-12-10 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_view', '0021_alter_quotationsubmissionitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotationsubmissionitem',
            name='price_valid_until',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='quotationsubmissionitem',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='quotationsubmissionitem',
            name='unit_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
