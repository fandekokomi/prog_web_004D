# Generated by Django 5.0.6 on 2024-06-27 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_historial_compra_total_clp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),
    ]