# Generated by Django 5.0.4 on 2024-05-12 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20240512_0231'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='habilitado',
        ),
    ]
