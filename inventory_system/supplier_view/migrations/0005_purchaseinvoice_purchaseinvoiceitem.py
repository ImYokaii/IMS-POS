# Generated by Django 5.0.7 on 2024-11-09 06:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_view', '0004_alter_quotationsubmission_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_no', models.CharField(max_length=50, unique=True)),
                ('supplier_company_name', models.CharField(max_length=255)),
                ('supplier_address', models.TextField()),
                ('date_issued', models.DateField()),
                ('due_date', models.DateField()),
                ('total_amount_payable', models.DecimalField(decimal_places=2, max_digits=10)),
                ('terms_and_condition', models.TextField()),
                ('status', models.CharField(max_length=50)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseInvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='supplier_view.purchaseinvoice')),
            ],
        ),
    ]
