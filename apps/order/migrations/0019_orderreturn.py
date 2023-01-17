# Generated by Django 3.2.16 on 2022-11-15 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0013_alter_partner_zone'),
        ('order', '0018_alter_order_zone'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderReturn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('return_counter', models.IntegerField(default=0)),
                ('return_status', models.CharField(blank=True, choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')], max_length=10, null=True)),
                ('oder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_returns', to='order.order')),
                ('order_line', models.ManyToManyField(to='order.Line')),
                ('return_partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_returns', to='partner.partner')),
            ],
        ),
    ]