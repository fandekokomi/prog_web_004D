# Generated by Django 5.0.6 on 2024-06-24 01:46

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_carrito'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitudp',
            name='imagen_producto',
            field=models.ImageField(upload_to=core.models.upload_to_temp),
        ),
    ]
