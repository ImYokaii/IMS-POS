# Generated by Django 5.0.7 on 2024-12-17 02:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement_view', '0031_purchaseorderitem_measurement_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorder',
            name='approved_by',
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='buyer_contact',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='prepared_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee', to=settings.AUTH_USER_MODEL),
        ),
    ]