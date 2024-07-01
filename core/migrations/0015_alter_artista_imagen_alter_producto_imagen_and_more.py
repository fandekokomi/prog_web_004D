# Generated by Django 5.0.6 on 2024-07-01 00:02

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_usuario_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artista',
            name='imagen',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=core.models.upload_to_artista),
        ),
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(max_length=255, upload_to=core.models.upload_to_producto),
        ),
        migrations.AlterField(
            model_name='solicituda',
            name='imagen_artista',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=core.models.upload_to_temp),
        ),
        migrations.AlterField(
            model_name='solicitudp',
            name='imagen_producto',
            field=models.ImageField(max_length=255, upload_to=core.models.upload_to_temp),
        ),
    ]