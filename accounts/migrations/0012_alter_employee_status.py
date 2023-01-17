# Generated by Django 3.2.16 on 2023-01-10 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_employee_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='status',
            field=models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('ACCEPT', 'Accept'), ('REJECTED', 'Rejected'), ('BLOCKED', 'Blocked')], max_length=50, null=True),
        ),
    ]