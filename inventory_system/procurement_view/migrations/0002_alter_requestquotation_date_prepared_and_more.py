# Generated by Django 5.0.7 on 2024-10-18 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement_view', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestquotation',
            name='date_prepared',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='RequestQuotationItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('request_quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='procurement_view.requestquotation')),
            ],
        ),
    ]
