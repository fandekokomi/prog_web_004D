# Generated by Django 5.0.4 on 2024-05-12 06:53

import core.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('biografia', models.TextField(blank=True, null=True)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to=core.models.upload_to_artista)),
                ('sitio_web', models.URLField(blank=True, null=True)),
                ('habilitado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_tipo', models.CharField(choices=[('cancion', 'Canción'), ('album', 'Álbum'), ('ep', 'EP')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TipoUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_tipo', models.CharField(choices=[('comun', 'Común'), ('miembro', 'Miembro'), ('admin', 'Admin')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('habilitado', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='core_usuario_groups', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='core_usuario_user_permissions', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('tipo_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tipousuario')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SolicitudA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('E', 'En Espera'), ('A', 'Aprobado'), ('R', 'Rechazado')], default='E', max_length=20)),
                ('nombre_artista', models.CharField(max_length=50)),
                ('fecha_nacimiento_artista', models.DateField(blank=True, null=True)),
                ('biografia_artista', models.TextField(blank=True, null=True)),
                ('imagen_artista', models.ImageField(blank=True, null=True, upload_to=core.models.upload_to_temp)),
                ('sitio_web_artista', models.URLField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SolicitudP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('E', 'En Espera'), ('A', 'Aprobado'), ('R', 'Rechazado')], default='E', max_length=20)),
                ('nombre_producto', models.CharField(max_length=100)),
                ('descripcion_producto', models.TextField()),
                ('imagen_producto', models.ImageField(blank=True, null=True, upload_to=core.models.upload_to_temp)),
                ('tipo_producto', models.CharField(choices=[('cancion', 'Canción'), ('album', 'Álbum'), ('ep', 'EP')], max_length=20)),
                ('precio_producto', models.IntegerField(default=0)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SolicitudesRechazadas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje_rechazo', models.TextField(blank=True, null=True)),
                ('solicitudA', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.solicituda')),
                ('solicitudP', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.solicitudp')),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=80)),
                ('descripcion', models.TextField()),
                ('imagen', models.ImageField(upload_to=core.models.upload_to_producto)),
                ('precio', models.IntegerField(default=0)),
                ('habilitado', models.BooleanField(default=True)),
                ('artista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.artista')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tipoproducto')),
            ],
        ),
    ]
