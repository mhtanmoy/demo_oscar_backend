# Generated by Django 3.2.16 on 2022-11-14 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_auto_20200801_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productalert',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
