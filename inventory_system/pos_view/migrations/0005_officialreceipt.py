# Generated by Django 5.0.7 on 2024-12-22 12:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos_view', '0004_salesinvoice_total_amount_with_vat_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OfficialReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_no', models.CharField(max_length=50, unique=True)),
                ('company_name', models.CharField(blank=True, default='AR. DJ Hardware Trading', max_length=255, null=True)),
                ('company_address', models.TextField(blank=True, default='street bergal maligaya park, 77 Bautista, Caloocan, Metro Manila', null=True)),
                ('receipt_date', models.DateField(auto_now_add=True)),
                ('vat', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total_amount_with_vat', models.DecimalField(decimal_places=2, max_digits=20)),
                ('issued_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issued_receipts', to=settings.AUTH_USER_MODEL)),
                ('sales_invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='official_receipt', to='pos_view.salesinvoice')),
            ],
        ),
    ]
