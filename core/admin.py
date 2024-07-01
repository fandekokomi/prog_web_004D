# admin.py
from django.contrib import admin
from .models import *
from admin_confirm import AdminConfirmMixin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UsuarioForm, UsuarioCreationForm

# Artista Admin
class ArtistaAdmin(AdminConfirmMixin, admin.ModelAdmin):
    confirm_change = True
    list_display = ('nombre', 'fecha_nacimiento', 'habilitado')
    list_filter = ('habilitado',)
    search_fields = ('nombre',)
    confirmation_fields = [
        'nombre', 
        'fecha_nacimiento', 
        'biografia', 
        'imagen', 
        'sitio_web', 
        'habilitado'
    ]

# TipoProducto Admin
class TipoProductoAdmin(AdminConfirmMixin, admin.ModelAdmin):
    confirm_change = True
    list_display = ('nom_tipo',)
    search_fields = ('nom_tipo',)
    confirmation_fields = ['nom_tipo']

# TipoUsuario Admin
class TipoUsuarioAdmin(AdminConfirmMixin, admin.ModelAdmin):
    confirm_change = True
    list_display = ('nom_tipo',)
    search_fields = ('nom_tipo',)
    confirmation_fields = ['nom_tipo']

# Producto Admin
class ProductoAdmin(AdminConfirmMixin, admin.ModelAdmin):
    confirm_change = True
    list_display = ('titulo', 'artista', 'tipo', 'precio', 'habilitado')
    list_filter = ('tipo', 'habilitado')
    search_fields = ('titulo', 'artista__nombre', 'tipo__nom_tipo')
    confirmation_fields = [
        'titulo', 
        'descripcion', 
        'imagen', 
        'artista', 
        'tipo', 
        'precio', 
        'habilitado'
    ]

# Usuario
class UsuarioAdmin(AdminConfirmMixin, BaseUserAdmin):
    form = UsuarioForm
    add_form = UsuarioCreationForm

    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Tipo de Usuario', {'fields': ('tipo_usuario',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'tipo_usuario'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)
    confirm_change = True
    confirmation_fields = [
        'username', 
        'email', 
        'password', 
        'is_staff', 
        'is_superuser', 
        'is_active', 
        'groups', 
        'user_permissions', 
        'tipo_usuario'
    ]

# SolicitudP Admin
class SolicitudPAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('usuario', 'estado', 'nombre_producto', 'tipo_producto', 'precio_producto')
    list_filter = ('estado', 'tipo_producto')
    search_fields = ('usuario__username', 'nombre_producto', 'tipo_producto')
    confirmation_fields = [
        'usuario', 
        'estado', 
        'nombre_producto', 
        'descripcion_producto', 
        'imagen_producto', 
        'artista_producto', 
        'tipo_producto', 
        'precio_producto'
    ]

# SolicitudA Admin
class SolicitudAAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('usuario', 'estado', 'nombre_artista', 'fecha_nacimiento_artista')
    list_filter = ('estado',)
    search_fields = ('usuario__username', 'nombre_artista')
    confirmation_fields = [
        'usuario', 
        'estado', 
        'nombre_artista', 
        'fecha_nacimiento_artista', 
        'biografia_artista', 
        'imagen_artista', 
        'sitio_web_artista'
    ]

# SolicitudesRechazadas Admin
class SolicitudesRechazadasAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('get_solicitud', 'mensaje_rechazo')
    search_fields = ('solicitudA__usuario__username', 'solicitudP__usuario__username')
    confirmation_fields = [
        'solicitudA', 
        'solicitudP', 
        'mensaje_rechazo'
    ]

    def get_solicitud(self, obj):
        if obj.solicitudA:
            return f"Solicitud de Artista #{obj.solicitudA.pk}"
        elif obj.solicitudP:
            return f"Solicitud de Producto #{obj.solicitudP.pk}"
        else:
            return "Sin solicitud relacionada"
    get_solicitud.short_description = 'Solicitud'

# Carrito Admin
class CarritoAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('usuario', 'producto')
    search_fields = ('usuario__username', 'producto__nombre')
    confirmation_fields = [
        'usuario', 
        'producto'
    ]

# historial_compra Admin
class historial_compraAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = ('usuario', 'fecha_compra', 'metodo_pago', 'total_clp', 'total_usd')
    list_filter = ('fecha_compra', 'metodo_pago')
    search_fields = ('usuario__username',)
    confirmation_fields = [
        'usuario', 
        'fecha_compra', 
        'metodo_pago', 
        'total_clp', 
        'total_usd', 
        'productos', 
        'cantidades_productos'
    ]

# Register your models here.
admin.site.register(Artista, ArtistaAdmin)
admin.site.register(TipoProducto, TipoProductoAdmin)
admin.site.register(TipoUsuario, TipoUsuarioAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(SolicitudP, SolicitudPAdmin)
admin.site.register(SolicitudA, SolicitudAAdmin)
admin.site.register(SolicitudesRechazadas, SolicitudesRechazadasAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(historial_compra, historial_compraAdmin)