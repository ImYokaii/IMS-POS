# Generated by Django 5.0.7 on 2024-11-09 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_view', '0008_remove_purchaseinvoice_due_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseinvoice',
            name='status',
            field=models.CharField(blank=True, default='Pending', max_length=50, null=True),
        ),
    ]