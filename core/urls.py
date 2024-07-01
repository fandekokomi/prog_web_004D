from django.urls import include, path
from .views import *
from rest_framework import routers

#URL APIS
router = routers.DefaultRouter()
router.register('artista', ArtistaViewSet)
router.register('producto', ProductoViewSet)

urlpatterns = [
    path('', index, name="index"),
    path('accounts/register/', register, name="register"),
    path('productos/', products, name="productos"),
    path('galeria/', gallery, name="galeria"),
    path('acerca/', about, name="acerca"),
    path('carrito/', carrito, name="carrito"),
    path('carrito/add/<int:producto_id>/', agregar_producto_carrito, name="carritoadd"),
    path('carrito/contadordeproductos/', cantidad_productos_carrito, name="carritocontador"),
    path('carrito/delete/<int:producto_id>/', eliminar_producto_carrito, name="carritodelete"),
    path('limpiar_carrito/', limpiar_carrito, name='limpiar_carrito'),
    path('compras/', historialcompra, name="historial_compra"),
    path('registrar_compra/', registrar_compra, name="registrar_compra"),
    path('generar_voucher/<int:compra_id>/', generar_voucher, name='generar_voucher'),
    path('miembros/', miembros, name="miembros"),
    path('artista/<int:artista_id>/', artista, name="artista"),
    path('solicitud/productos/', solicitudP, name="solicitudP"),
    path('solicitud/artista/', solicitudA, name="solicitudA"),
    path('solicitud/editar-p/<int:solicitud_id>/', editar_solicitud_p, name="editar_solicitud-p"),
    path('solicitud/editar-a/<int:solicitud_id>/', editar_solicitud_a, name="editar_solicitud-a"),
    path('administradores/', listar_para_administradores, name="administradores"),
    path('administradores/solicitudes/', administradores, name="solicitudes_admin"),
    path('administradores/agregar-artista/', agregar_artista, name="agregar_artista"),
    path('administradores/agregar-producto/', agregar_producto, name="agregar_producto"),
    path('administradores/agregar-miembro/', agregar_miembro, name="agregar_miembro"),
    path('administradores/rechazar-a/<int:solicitud_id>/', rechazar_solicitud_a, name="rechazar_solicitud-a"),
    path('administradores/rechazar-p/<int:solicitud_id>/', rechazar_solicitud_p, name="rechazar_solicitud-p"),
    path('administradores/aprobar-a/<int:solicitud_id>/', aprobar_solicitud_a, name="aprobar_solicitud-a"),
    path('administradores/aprobar-p/<int:solicitud_id>/', aprobar_solicitud_p, name="aprobar_solicitud-p"),
    path('administradores/editar-a/<int:artista_id>/', editar_artista, name="editar_artista"),
    path('administradores/quitarimg-a/<int:artista_id>/', quitar_imagen_artista, name="quitar_img_artista"),
    path('administradores/editar-p/<int:producto_id>/', editar_producto, name="editar_producto"),
    path('administradores/editar-m/<int:miembro_id>/', editar_miembro, name="editar_miembro"),
    path('administradores/eliminar-a/<int:artista_id>/', eliminar_artista, name="eliminar_artista"),
    path('administradores/eliminar-p/<int:producto_id>/', eliminar_producto, name="eliminar_producto"),
    path('administradores/eliminar-m/<int:miembro_id>/', eliminar_miembro, name="eliminar_miembro"),
    path('administradores/enable_or_disable_artista/<int:artista_id>/', enable_or_disable_artista, name="enable_or_disable_artista"),
    path('administradores/enable_or_disable_producto/<int:producto_id>/', enable_or_disable_producto, name="enable_or_disable_producto"),
    path('administradores/enable_or_disable_miembro/<int:miembro_id>/', enable_or_disable_miembro, name="enable_or_disable_miembro"),
    #APIS
    path('api/', include(router.urls)),
    #API LAST_FM
    path('lastfm_api/', lastfm_api, name="lastfm_api"),
    #ACCOUNT LOCKED
    path('locked/', locked, name="locked"),
]