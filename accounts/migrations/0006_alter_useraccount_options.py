# Generated by Django 3.2.16 on 2022-12-30 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_useraccount_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useraccount',
            options={'permissions': (('test_tahseen_bhai', 'Can view Tahseen Bhai'),)},
        ),
    ]
