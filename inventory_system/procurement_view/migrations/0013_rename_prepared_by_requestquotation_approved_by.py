# Generated by Django 5.0.7 on 2024-11-23 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('procurement_view', '0012_alter_purchaseorderitem_purchase_order'),
    ]

    operations = [
        migrations.RenameField(
            model_name='requestquotation',
            old_name='prepared_by',
            new_name='approved_by',
        ),
    ]
