# Generated by Django 5.0.7 on 2024-11-22 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos_view', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesinvoiceitem',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='salesinvoiceitem',
            name='product_id',
        ),
        migrations.DeleteModel(
            name='SalesInvoice',
        ),
        migrations.DeleteModel(
            name='SalesInvoiceItem',
        ),
    ]