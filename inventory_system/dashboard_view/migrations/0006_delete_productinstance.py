# Generated by Django 5.0.7 on 2024-11-23 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_view', '0005_productinstance_is_favorite'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductInstance',
        ),
    ]