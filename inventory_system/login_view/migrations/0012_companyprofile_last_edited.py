# Generated by Django 5.0.7 on 2024-12-27 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_view', '0011_rename_userprofile_companyprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyprofile',
            name='last_edited',
            field=models.DateField(blank=True, null=True),
        ),
    ]
