# Generated by Django 3.2.16 on 2022-11-14 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0011_zone'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='partner.zone'),
        ),
    ]
