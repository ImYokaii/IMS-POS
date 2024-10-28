# Generated by Django 5.0.7 on 2024-10-15 14:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestQuotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_company_name', models.CharField(max_length=255)),
                ('buyer_address', models.CharField(max_length=255)),
                ('buyer_contact', models.CharField(max_length=100)),
                ('quotation_no', models.CharField(max_length=50, unique=True)),
                ('prepared_by', models.CharField(max_length=100)),
                ('quote_valid_until', models.DateField()),
                ('date_prepared', models.DateField()),
                ('terms_and_conditions', models.TextField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(max_length=50)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]