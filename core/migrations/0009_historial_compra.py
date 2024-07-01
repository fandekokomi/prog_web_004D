# Generated by Django 5.0.6 on 2024-06-26 06:31

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_solicitudp_imagen_producto'),
    ]

    operations = [
        migrations.CreateModel(
            name='historial_compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_compra', models.DateField(default=django.utils.timezone.now)),
                ('metodo_pago', models.CharField(max_length=20)),
                ('total_clp', models.IntegerField()),
                ('total_usd', models.IntegerField()),
                ('productos', models.ManyToManyField(to='core.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]