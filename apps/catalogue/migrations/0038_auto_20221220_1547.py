# Generated by Django 3.2.16 on 2022-12-20 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0037_auto_20221220_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promocode',
            name='minimum_applied',
        ),
        migrations.AddField(
            model_name='promocode',
            name='maximum_applied',
            field=models.IntegerField(default=0),
        ),
    ]
