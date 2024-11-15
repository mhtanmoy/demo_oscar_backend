# Generated by Django 3.2.16 on 2022-11-27 12:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_deliveryman_sub_zone'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('nid', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.FileField(blank=True, null=True, upload_to='employee')),
                ('shift_start_hour', models.TimeField(blank=True, null=True)),
                ('shift_end_hour', models.TimeField(blank=True, null=True)),
                ('phone', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=150)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('employee_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='accounts.employeecategory')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
