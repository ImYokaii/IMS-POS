# Generated by Django 5.0.7 on 2024-11-23 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_view', '0023_rename_user_wasteproduct_employee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wasteproduct',
            old_name='employee',
            new_name='user',
        ),
    ]
