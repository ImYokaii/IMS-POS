# Generated by Django 5.0.7 on 2024-11-03 07:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_view', '0002_alter_quotationsubmission_quotation_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quotationsubmission',
            name='total_amount',
        ),
    ]
