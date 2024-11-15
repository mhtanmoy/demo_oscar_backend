# Generated by Django 3.2.16 on 2022-12-31 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0017_partner_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='subzone',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='zone',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
