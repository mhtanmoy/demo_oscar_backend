# Generated by Django 3.2.16 on 2022-12-31 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0022_alter_orderreturn_return_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordercountperschedule',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]