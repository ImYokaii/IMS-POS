# Generated by Django 5.0.7 on 2024-12-10 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_view', '0014_quotationsubmission_request_quotation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotationsubmission',
            name='buyer_address',
            field=models.TextField(default='street bergal maligaya park, 77 Bautista, Caloocan, Metro Manila'),
        ),
        migrations.AlterField(
            model_name='quotationsubmission',
            name='buyer_company_name',
            field=models.CharField(default='AR. DJ Hardware Trading', max_length=255),
        ),
    ]
