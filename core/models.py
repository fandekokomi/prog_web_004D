from django.utils import timezone
import os
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

def upload_to_artista(instance, filename):
    # Eliminar caracteres especiales del nombre del artista
    nombre_limpio = re.sub(r'\W+', '', instance.nombre, flags=re.UNICODE)
    return f'artistas/{nombre_limpio}/{filename}'

def upload_to_producto(instance, filename):
    # Eliminar caracteres especiales del nombre del artista y del título del producto
    nombre_limpio = re.sub(r'\W+', '', instance.artista.nombre, flags=re.UNICODE)
    titulo_limpio = re.sub(r'\W+', '', instance.titulo, flags=re.UNICODE)
    return f'productos/{nombre_limpio}/{titulo_limpio}/{filename}'

def upload_to_temp(instance, filename):
    # Determinar el tipo de solicitud y el ID
    if isinstance(instance, SolicitudP):
        tipo_solicitud = 'P'
    elif isinstance(instance, SolicitudA):
        tipo_solicitud = 'A'
    else:
        raise ValueError("Tipo de instancia de solicitud desconocido.")

    if instance.pk:
        solicitud_id = instance.pk
    else:
        solicitud_id = 'TEMP'

    return f'temp/solicitudes/{instance.usuario.username}/{tipo_solicitud}/{solicitud_id}/{filename}'

class Artista(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    biografia = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to=upload_to_artista, null=True, blank=True, max_length=255)
    sitio_web = models.URLField(null=True, blank=True)
    habilitado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    def biografia_breve(self):
        return ' '.join(self.biografia.split('.')[:2]) + '.'
    def nombreimagen(self):
        return os.path.basename(self.imagen.name)

class TipoProducto(models.Model):
    TIPO_CHOICES = [
        ('cancion', 'Canción'),
        ('album', 'Álbum'),
        ('ep', 'EP'),
    ]

    nom_tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return dict(self.TIPO_CHOICES)[self.nom_tipo]

class Producto(models.Model):
    titulo = models.CharField(max_length=80)
    descripcion = models.TextField(null=False, blank=False)
    imagen = models.ImageField(upload_to=upload_to_producto, blank=False, null=False, max_length=255)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
    precio = models.IntegerField(default=0)
    habilitado = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    def descripcion_breve(self):
        # Elimina los puntos al inicio del texto
        descripcion = self.descripcion.lstrip('.')
        # Divide el texto en frases
        frases = [frase for frase in descripcion.split('.') if frase]
        # Une las dos primeras frases
        return ' '.join(frases[:2]) + '.'

    def precio_clp(self):
        return "${:,.0f}".format(self.precio).replace(",", ".")
    
    def nombreimagen(self):
        return os.path.basename(self.imagen.name)
    
    def obtener_descripcion_formateada(self):
        # Aquí realizas cualquier formateo necesario
        # Por ejemplo, reemplazando '\n' con '<br>' para saltos de línea
        return self.descripcion.replace('\n', '<br>')
    
class TipoUsuario(models.Model):
    TIPO_CHOICES = [
        ('comun', 'Común'),
        ('miembro', 'Miembro'),
        ('admin', 'Admin'),
    ]
    nom_tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nom_tipo

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, tipo_usuario=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, tipo_usuario=tipo_usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, tipo_usuario=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        tipo_usuario, created = TipoUsuario.objects.get_or_create(nom_tipo='admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if tipo_usuario is None:
            raise ValueError('Superuser must have a tipo_usuario.')

        extra_fields['tipo_usuario'] = tipo_usuario

        return self.create_user(username, email, password, **extra_fields)
    
class Usuario(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="core_usuario_groups",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="core_usuario_user_permissions",
        related_query_name="user",
    )

    objects = UsuarioManager()

    def save(self, *args, **kwargs):
        if self.pk is None:
            if not self.password.startswith('pbkdf2_sha256$'):
                self.set_password(self.password)
        else:
            original_usuario = Usuario.objects.get(pk=self.pk)
            if self.password != original_usuario.password:
                if not self.password.startswith('pbkdf2_sha256$'):
                    self.set_password(self.password)
        super(Usuario, self).save(*args, **kwargs)

    def __str__(self):
        return self.username
    
class SolicitudP(models.Model):
    ESTADO_CHOICES = [
        ('E', 'En Espera'),
        ('A', 'Aprobado'),
        ('R', 'Rechazado'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='E')
    nombre_producto = models.CharField(max_length=100)
    descripcion_producto = models.TextField()
    imagen_producto = models.ImageField(blank=False, null=False, upload_to=upload_to_temp, max_length=255)
    artista_producto = models.ForeignKey(Artista, on_delete=models.CASCADE, default=None)
    tipo_producto = models.CharField(max_length=20, choices=TipoProducto.TIPO_CHOICES)
    precio_producto = models.IntegerField(default=0)

    def __str__(self):
        return f"Solicitud #{self.pk} de {self.usuario.username} - {self.tipo_producto}: {self.nombre_producto}"
    
class SolicitudA(models.Model):
    ESTADO_CHOICES = [
        ('E', 'En Espera'),
        ('A', 'Aprobado'),
        ('R', 'Rechazado'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='E')
    nombre_artista = models.CharField(max_length=50)
    fecha_nacimiento_artista = models.DateField(null=True, blank=True)
    biografia_artista = models.TextField(null=True, blank=True)
    imagen_artista = models.ImageField(null=True, blank=True, upload_to=upload_to_temp, max_length=255)
    sitio_web_artista = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Solicitud #{self.pk} de {self.usuario.username} - Artista: {self.nombre_artista}"

class SolicitudesRechazadas(models.Model):
    solicitudA = models.ForeignKey(SolicitudA, on_delete=models.CASCADE, null=True, blank=True)
    solicitudP = models.ForeignKey(SolicitudP, on_delete=models.CASCADE, null=True, blank=True)
    mensaje_rechazo = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.solicitudA and self.solicitudP:
            raise ValidationError("Una solicitud rechazada no puede estar relacionada con ambas solicitudes (SolicitudA y SolicitudP) al mismo tiempo.")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.solicitudA:
            return f"Rechazo #{self.pk} - SolicitudA #{self.solicitudA.pk}"
        elif self.solicitudP:
            return f"Rechazo #{self.pk} - SolicitudP #{self.solicitudP.pk}"
        else:
            return f"Rechazo #{self.pk} - Sin solicitud relacionada"
    

class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

class historial_compra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_compra = models.DateField(default=timezone.now)
    metodo_pago = models.CharField(max_length=20)
    total_clp = models.CharField(max_length=10)
    total_usd = models.CharField(max_length=10)
    productos = models.ManyToManyField(Producto)
    cantidades_productos = models.JSONField(default=dict)

    def str(self):
        return f"Pago de {self.usuario.username} el {self.fecha_compra}"
