# Generated by Django 5.0.7 on 2024-12-10 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_view', '0020_alter_quotationsubmissionitem_price_valid_until'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotationsubmissionitem',
            name='quantity',
            field=models.IntegerField(null=True),
        ),
    ]
