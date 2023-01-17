# Generated by Django 3.2.16 on 2022-11-14 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0013_alter_partner_zone'),
        ('order', '0017_order_zone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='partner.zone'),
        ),
    ]
