import shutil
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login
from .models import *
from .forms import *
import os
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from PIL import Image, ImageOps
import re
from django.conf import settings
from .utils import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .decorators import usuario_de_tipo
import asyncio
import cloudinary.uploader
from io import BytesIO

def get_artistaysusproductoshabilitados(artista_id):
    aux = {}
    try:
        este_artista = Artista.objects.get(pk=artista_id)
        aux['este_artista'] = este_artista
    except Artista.DoesNotExist:
        return aux

    try:
        tipo1 = TipoProducto.objects.get(nom_tipo='cancion')
        s = Producto.objects.filter(habilitado=True, tipo=tipo1, artista=este_artista)
        aux['productos_sencillos'] = s
    except TipoProducto.DoesNotExist:
        pass

    try:
        tipo2 = TipoProducto.objects.get(nom_tipo='album')
        a = Producto.objects.filter(habilitado=True, tipo=tipo2, artista=este_artista)
        aux['productos_albums'] = a
    except TipoProducto.DoesNotExist:
        pass

    try:
        tipo3 = TipoProducto.objects.get(nom_tipo='ep')
        e = Producto.objects.filter(habilitado=True, tipo=tipo3, artista=este_artista)
        aux['productos_eps'] = e
    except TipoProducto.DoesNotExist:
        pass

    return aux

def get_artistasyproductoshabilitados():
    aux = {}
    try:
        tipo1 = TipoProducto.objects.get(nom_tipo='cancion')
        aux['productos_sencillos'] = Producto.objects.filter(habilitado=True, tipo=tipo1).order_by('pk')
    except TipoProducto.DoesNotExist:
        pass

    try:
        tipo2 = TipoProducto.objects.get(nom_tipo='album')
        aux['productos_albums'] = Producto.objects.filter(habilitado=True, tipo=tipo2).order_by('pk')
    except TipoProducto.DoesNotExist:
        pass

    try:
        tipo3 = TipoProducto.objects.get(nom_tipo='ep')
        aux['productos_eps'] = Producto.objects.filter(habilitado=True, tipo=tipo3).order_by('pk')
    except TipoProducto.DoesNotExist:
        pass

    if Artista.objects.filter(habilitado=True).exists():
        aux['artistas'] = Artista.objects.filter(habilitado=True).order_by('pk')

    return aux

def get_info_modals():

    modal_mimori = get_object_or_404(Producto, pk=11)
    modal_akari = get_object_or_404(Producto, pk=18)
    modal_tomori = get_object_or_404(Producto, pk=17)

    return {
        'modal_mimori': modal_mimori,
        'modal_akari': modal_akari,
        'modal_tomori': modal_tomori
    }

#VIEWSETS
class ArtistaViewSet(viewsets.ModelViewSet):
    queryset = Artista.objects.all().order_by('pk')
    serializer_class = ArtistaSerializer
    renderer_classes = [JSONRenderer]

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('pk')
    serializer_class = ProductoSerializer
    renderer_classes = [JSONRenderer]

#API LAST_FM
def lastfm_api(request):
    # Obtener la lista de artistas japoneses
    lastfm_api = get_japanese_artists()
    
    # Configurar la paginación
    paginator = Paginator(lastfm_api, 5)  # Mostrar 5 artistas por página
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    page_obj = paginator.get_page(page_number)  # Obtener el objeto de la página actual
    
    # Pasar el objeto de la página al template
    return render(request, 'core/apis/artista/artistas_api.html', {'page_obj': page_obj})

#VISTAS GENERALES:
def index(request):
    try:
        aux = get_artistasyproductoshabilitados()
        aux2 = get_info_modals()
        
        # Combinar los diccionarios
        context = {**aux, **aux2}
    except:
        context = None

    return render(request, 'core/index.html', context)
def register(request):
    aux = {
        'form': registerForm()
    }
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            tipo = get_object_or_404(TipoUsuario, nom_tipo='comun')
            user = form.save(commit=False)
            user.tipo_usuario = tipo
            user.save()
            group, created = Group.objects.get_or_create(name='comun')
            user.groups.add(group)
            user.save()
            #user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            #login(request, user)
            return redirect('index')
        else:
            aux['form'] = form
    return render(request, 'registration/register.html', aux)
def products(request):
    try:
        aux = get_artistasyproductoshabilitados()
    except:
        aux = None
    return render(request, 'core/products.html', aux)
def gallery(request):
    productos_list = Producto.objects.filter(habilitado=True).order_by('pk')
    paginator = Paginator(productos_list, 6) # Muestra 6 productos por página

    page_number = request.GET.get('page')
    productos_all = paginator.get_page(page_number)
    aux = {
        'productos_all': productos_all
    }
    return render(request, 'core/gallery.html', aux)
def about(request):
    return render(request, 'core/about.html')
def carrito(request):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        aux = {
            'carrito': Carrito.objects.filter(usuario=request.user)
        }
    else:
        messages.error(request, '¡Por favor inicie sesión para comenzar a agregar productos al carrito!')
        aux = None
    return render(request, 'core/carrito.html', aux)
def agregar_producto_carrito(request, producto_id):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        producto = get_object_or_404(Producto, pk=producto_id)
        if Carrito.objects.filter(usuario=request.user, producto=producto):
            messages.error(request, '¡El producto ya está en el carrito!')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            c = Carrito(
                usuario = request.user, 
                producto = producto
                )
            c.save()
            messages.success(request, '¡Producto agregado correctamente!')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, '¡Debe haber iniciado sesión para agregar el producto al carrito!')
    return redirect(request.META.get('HTTP_REFERER'))
def eliminar_producto_carrito(request, producto_id):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        producto = get_object_or_404(Producto, pk=producto_id)
        item = Carrito.objects.filter(usuario=request.user, producto=producto)
        if item:
            item.delete()
        else:
            messages.error(request, '¡El producto no existe en el carrito!')
            return redirect('carrito')
    else:
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('carrito')
def cantidad_productos_carrito(request):
    if request.user.is_authenticated:
        try:
            contador = Carrito.objects.filter(usuario=request.user).count()
        except Exception as e:
            print(e)
            contador = 0
    else:
        contador = 0
    return contador
@login_required
def limpiar_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user)
    carrito.delete()
    return redirect('carrito')

def artista(request, artista_id):
    try:
        aux = get_artistaysusproductoshabilitados(artista_id)
    except:
        aux = None
    return render(request, 'core/artista.html', aux)
#VISTAS DE MIEMBROS
@usuario_de_tipo('miembro')
def miembros(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario == 'comun':
            return redirect('index')
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
        solicitudA = SolicitudA.objects.filter(usuario=request.user)
        solicitudP = SolicitudP.objects.filter(usuario=request.user)
        solicitudesArechazadas = SolicitudesRechazadas.objects.filter(solicitudA__in=solicitudA)
        solicitudesPrechazadas = SolicitudesRechazadas.objects.filter(solicitudP__in=solicitudP)
        aux = {
            'listaA' : solicitudA,
            'listaP' : solicitudP,
            'listaRA' : solicitudesArechazadas,
            'listaRP' : solicitudesPrechazadas
        }
        return render(request, 'core/miembros/members.html', aux)
    else:
        return redirect('index')
def solicitudP(request):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    aux = {'form': SolicitudPForm()}

    if request.method == 'POST':
        form = SolicitudPForm(request.POST, request.FILES)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.imagen_producto = None  # Asegúrate de que la imagen no se guarde en este punto
            solicitud.save()  # Guarda la instancia primero para obtener un ID

            # Asigna la imagen a la instancia después de que se haya creado
            if 'imagen_producto' in request.FILES:
                image_file = request.FILES['imagen_producto']
                solicitud.imagen_producto.save(image_file.name, ContentFile(image_file.read()), save=True)

            messages.success(request, "¡Solicitud enviada correctamente!")
            return redirect('miembros')
        else:
            aux['form'] = form
            messages.error(request, "¡El formulario no es válido!")

    return render(request, 'core/miembros/solicitudes/requestP.html', aux)
def solicitudA(request):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    
    aux = {'form': SolicitudAForm()}

    if request.method == 'POST':
        form = SolicitudAForm(request.POST, request.FILES)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.imagen_artista = None  # Asegúrate de que la imagen no se guarde en este punto
            solicitud.save()  # Guarda la instancia primero para obtener un ID

            # Asigna la imagen a la instancia después de que se haya creado
            if 'imagen_artista' in request.FILES:
                image_file = request.FILES['imagen_artista']
                solicitud.imagen_artista.save(image_file.name, ContentFile(image_file.read()), save=True)

            messages.success(request, "¡Solicitud enviada correctamente!")
            return redirect('miembros')
        else:
            aux['form'] = form
            messages.error(request, "¡El formulario no es válido!")

    return render(request, 'core/miembros/solicitudes/requestA.html', aux)
def editar_solicitud_p(request, solicitud_id):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    
    solicitud = get_object_or_404(SolicitudP, pk=solicitud_id)
    
    if solicitud.estado in ('E', 'R'):
        aux = {'form': SolicitudPForm(instance=solicitud)}

        if request.method == 'POST':
            if 'imagen_producto' in request.FILES:
                if solicitud.imagen_producto:
                    if os.path.isfile(solicitud.imagen_producto.path):
                        os.remove(solicitud.imagen_producto.path)
                        solicitud.imagen_producto.delete(save=False)
            
            form = SolicitudPForm(request.POST, request.FILES, instance=solicitud)
            if form.is_valid():
                if solicitud.estado == 'R':
                    solicitudRechazada = get_object_or_404(SolicitudesRechazadas, solicitudP=solicitud)
                    solicitudRechazada.delete()
                    solicitud.estado = 'E'
                    solicitud.save()
                    form.save()
                else:
                    solicitud.save()
                    form.save()
                
                # Mensaje de éxito
                messages.success(request, "¡Solicitud actualizada correctamente!")
                return redirect('miembros')
            else:
                aux['form'] = form
                # Mensaje de error
                messages.error(request, "¡Error al actualizar su solicitud!")
    else:
        return redirect('miembros')

    return render(request, 'core/miembros/crud/updateP.html', aux)
def editar_solicitud_a(request, solicitud_id):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    
    solicitud = get_object_or_404(SolicitudA, pk=solicitud_id)
    
    if solicitud.estado in ('E', 'R'):
        aux = {'form': SolicitudAForm(instance=solicitud)}

        if request.method == 'POST':
            if 'imagen_artista' in request.FILES:
                if solicitud.imagen_artista:
                    if os.path.isfile(solicitud.imagen_artista.path):  # Verifica si el archivo existe en el sistema de archivos
                        os.remove(solicitud.imagen_artista.path)
                        solicitud.imagen_artista.delete(save=False)
            
            form = SolicitudAForm(request.POST, request.FILES, instance=solicitud)
            if form.is_valid():
                if solicitud.estado == 'R':
                    solicitudRechazada = get_object_or_404(SolicitudesRechazadas, solicitudA=solicitud)
                    solicitudRechazada.delete()
                    solicitud.estado = 'E'
                    solicitud.save()
                    form.save()
                else:
                    solicitud.save()
                    form.save()
                
                # Mensaje de éxito
                messages.success(request, "¡Solicitud actualizada correctamente!")
                return redirect('miembros')  # Redirigir a la vista que se desee después de una actualización exitosa
            else:
                aux['form'] = form
                # Mensaje de error
                messages.error(request, "¡Error al actualizar su solicitud!")
    else:
        return redirect('miembros')

    return render(request, 'core/miembros/crud/updateA.html', aux)

#VISTAS DE ADMINISTRADORES
@usuario_de_tipo('admin')
def administradores(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario.nom_tipo == 'comun' or request.user.tipo_usuario.nom_tipo == 'miembro':
            return redirect('index')
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
        solicitudA = SolicitudA.objects.filter(estado='E')
        solicitudP = SolicitudP.objects.filter(estado='E')
        aux = {
            'listaA' : solicitudA,
            'listaP' : solicitudP,
        }

        return render(request, 'core/administradores/admin.html', aux)
    else:
        return redirect('index')
def rechazar_solicitud_a(request, solicitud_id):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    
    solicitud = get_object_or_404(SolicitudA, pk=solicitud_id)
    aux = {'form': SolicitudesRechazadasAForm(initial={'solicitudA': solicitud})}
    
    if request.method == 'POST':
        form = SolicitudesRechazadasAForm(request.POST, initial={'solicitudA': solicitud})
        if form.is_valid():
            solicitud.estado = 'R'
            solicitud_rechazada = form.save(commit=False)
            # Asignar la solicitud asociada
            solicitud_rechazada.solicitudA = solicitud
            # Guardar la instancia en la base de datos
            solicitud_rechazada.save()
            solicitud.save()
            
            # Mensaje de éxito
            messages.success(request, "Solicitud rechazada correctamente.")
            return redirect('administradores')
        else:
            aux['form'] = form
            # Mensaje de error
            messages.error(request, "Error al rechazar la solicitud. Verifique los datos ingresados.")

    return render(request, 'core/administradores/solicitudes/rechazarA.html', aux)
def rechazar_solicitud_p(request, solicitud_id):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    
    solicitud = get_object_or_404(SolicitudP, pk=solicitud_id)
    aux = {'form': SolicitudesRechazadasPForm(initial={'solicitudP': solicitud})}
    
    if request.method == 'POST':
        form = SolicitudesRechazadasPForm(request.POST, initial={'solicitudP': solicitud})
        if form.is_valid():
            solicitud.estado = 'R'
            solicitud_rechazada = form.save(commit=False)
            # Asignar la solicitud asociada
            solicitud_rechazada.solicitudP = solicitud
            # Guardar la instancia en la base de datos
            solicitud_rechazada.save()
            solicitud.save()
            
            # Mensaje de éxito
            messages.success(request, "Solicitud rechazada correctamente.")
            return redirect('administradores')
        else:
            aux['form'] = form
            # Mensaje de error
            messages.error(request, "Error al rechazar la solicitud. Verifique los datos ingresados.")
    
    return render(request, 'core/administradores/solicitudes/rechazarP.html', aux)
def aprobar_solicitud_a(request, solicitud_id):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    
    solicitud = get_object_or_404(SolicitudA, pk=solicitud_id)
    form = AprobarSolicitudForm(request.POST or None, initial={'solicitud_id': solicitud_id})
    
    if request.method == 'POST':
        if form.is_valid():
            solicitud.estado = 'A'
            artista = Artista(
                nombre=solicitud.nombre_artista,
                fecha_nacimiento=solicitud.fecha_nacimiento_artista,
                biografia=solicitud.biografia_artista,
                sitio_web=solicitud.sitio_web_artista
            )
            artista.save()
            
            # Copiar la imagen de la solicitud a la ubicación de almacenamiento de artistas
            if solicitud.imagen_artista:
                nombre_archivo = os.path.basename(solicitud.imagen_artista.name)
                ruta_artista = os.path.join('artistas', artista.nombre, nombre_archivo)
                os.makedirs(os.path.dirname(ruta_artista), exist_ok=True)
                
                with open(solicitud.imagen_artista.path, 'rb') as origen, open(ruta_artista, 'wb') as destino:
                    shutil.copyfileobj(origen, destino)
                
                artista.imagen = ruta_artista
                artista.save()
                
                # Eliminar archivo original en la ruta de origen
                os.remove(solicitud.imagen_artista.path)
                solicitud.imagen_artista.delete()
            
            solicitud.save()
            # Mensaje de éxito
            messages.success(request, "¡Solicitud aprobada y Artista agregado correctamente!")
            return redirect('administradores')
        else:
            # Mensaje de error
            messages.error(request, "Hubo un problema al procesar el formulario.")
    
    return render(request, 'core/administradores/solicitudes/aprobarA.html', {'form': form, 'solicitud': solicitud})
def aprobar_solicitud_p(request, solicitud_id):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    
    solicitud = get_object_or_404(SolicitudP, pk=solicitud_id)
    form = AprobarSolicitudForm(request.POST or None, initial={'solicitud_id': solicitud_id})
    
    if request.method == 'POST':
        if form.is_valid():
            solicitud.estado = 'A'
            tipo = get_object_or_404(TipoProducto, nom_tipo=solicitud.tipo_producto)
            producto = Producto(
                titulo=solicitud.nombre_producto,
                descripcion=solicitud.descripcion_producto,
                artista=solicitud.artista_producto,
                tipo=tipo,
                precio=solicitud.precio_producto
            )
            producto.save()
            
            if solicitud.imagen_producto:
                nombre_archivo = os.path.basename(solicitud.imagen_producto.name)
                ruta_producto = os.path.join('productos', producto.artista.nombre, producto.titulo, nombre_archivo)
                os.makedirs(os.path.dirname(ruta_producto), exist_ok=True)
                
                with open(solicitud.imagen_producto.path, 'rb') as origen, open(ruta_producto, 'wb') as destino:
                    shutil.copyfileobj(origen, destino)
                
                producto.imagen = ruta_producto
                producto.save()
                
                # Eliminar archivo original en la ruta de origen
                os.remove(solicitud.imagen_producto.path)
                solicitud.imagen_producto.delete()
            
            solicitud.save()
            
            # Mensaje de éxito
            if producto.tipo.nom_tipo == "cancion":
                messages.success(request, f"¡Solicitud aprobada y {producto.tipo.nom_tipo} agregada correctamente!")
            else:
                messages.success(request, f"¡Solicitud aprobada y {producto.tipo.nom_tipo} agregado correctamente!")
            
            return redirect('administradores')
        else:
            # Mensaje de error
            messages.error(request, "Hubo un problema al procesar el formulario.")
    
    return render(request, 'core/administradores/solicitudes/aprobarP.html', {'form': form, 'solicitud': solicitud})
@usuario_de_tipo('admin')
def agregar_artista(request):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True
    
    aux = {'form': ArtistaForm()}
    
    if request.method == 'POST':
        form = ArtistaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Mensaje de éxito
            messages.success(request, "¡Artista agregado con éxito!")
            return redirect('administradores')
        else:
            aux['form'] = form
            # Mensaje de error
            messages.error(request, "¡El formulario no es válido!")
    
    return render(request, 'core/administradores/crud/addA.html', aux)
def editar_artista(request, artista_id):
    artista = get_object_or_404(Artista, pk=artista_id)
    aux = {
        'form': ArtistaForm(instance=artista)
    }

    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True

    if request.method == 'POST':
        form = ArtistaForm(request.POST, request.FILES, instance=artista)
        if form.is_valid():
            # Obtener la instancia del formulario antes de guardar
            old_artista = form.save(commit=False)

            if old_artista.imagen and artista.imagen and old_artista.imagen != artista.imagen:
                # Si se ha cambiado la imagen y existe una imagen antigua
                if artista.imagen.name:
                    # Obtener el public_id de Cloudinary a partir de la URL de la imagen
                    # La URL de Cloudinary tiene el formato: https://res.cloudinary.com/<cloud_name>/image/upload/<public_id>/<file_name>
                    image_url = artista.imagen.url
                    public_id = image_url.split('/v1/media/')[1].split('/')[1].split('.')[0]
                    cloudinary.uploader.destroy(public_id, resource_type='image')

            # Guardar los cambios
            form.save()
            # Mensaje de éxito
            messages.success(request, "¡Artista actualizado correctamente!")
            return redirect('administradores')  # Redirigir a la página de administradores o donde corresponda
        else:
            aux['form'] = form
            # Mensaje de error
            messages.error(request, "¡El formulario no es válido!")

    return render(request, 'core/administradores/crud/updateA.html', aux)
def quitar_imagen_artista(request, artista_id):
    artista = get_object_or_404(Artista, pk=artista_id)
    if artista.imagen:
        if artista.imagen.name:
            # Obtener el public_id de Cloudinary a partir de la URL de la imagen
            image_url = artista.imagen.url
            public_id = image_url.split('/v1/media/')[1].split('/')[1].split('.')[0]
            
            # Eliminar la imagen en Cloudinary
            cloudinary.uploader.destroy(public_id, resource_type='image')

            # Eliminar la imagen del modelo
            artista.imagen.delete(save=False)
            artista.save()

            messages.success(request, 'La imagen fue eliminada correctamente.')
        else:
            messages.error(request, 'La imagen no se encuentra en Cloudinary.')
    else:
        messages.error(request, 'No hay imagen para eliminar.')

    return redirect('administradores')
@usuario_de_tipo('admin')
def eliminar_artista(request, artista_id):
    artista = Artista.objects.get(pk=artista_id)
    artista.delete()
    messages.success(request, 'Artista eliminado correctamente.')
    return redirect('administradores')
def enable_or_disable_artista(request, artista_id):
    artista = get_object_or_404(Artista, pk=artista_id)
    frase = ""
    if artista.habilitado:
        artista.habilitado = False
        frase = "deshabilitado"
    else:
        artista.habilitado = True
        frase = "habilitado"
    artista.save()
    
    # Devolver una respuesta JSON con un mensaje y el nuevo estado del artista
    data = {
        'message': f'¡Artista {frase} con éxito!',
        'habilitado': artista.habilitado
    }
    return JsonResponse(data)
@usuario_de_tipo('admin')
def agregar_producto(request):
    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True

    # Crea tipos de productos si no existen
    if not TipoProducto.objects.exists():
        tipos = ['cancion', 'album', 'ep']  # Reemplaza esto con tus tipos de productos
        for tipo in tipos:
            TipoProducto.objects.create(nom_tipo=tipo)
    
    aux = {'form': ProductoForm()}

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Mensaje de éxito
            messages.success(request, "¡Producto agregado con éxito!")
            return redirect('administradores')
        else:
            aux['form'] = form
            # Mensaje de error
            messages.error(request, "¡El formulario no es válido!")

    return render(request, 'core/administradores/crud/addP.html', aux)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)

    # Limpia los mensajes después de haber sido mostrados
    storage = messages.get_messages(request)
    storage.used = True

    aux = {
        'form': ProductoForm(instance=producto)
    }

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            # Obtener la instancia del formulario antes de guardar
            old_producto = form.save(commit=False)

            if old_producto.imagen and producto.imagen and old_producto.imagen != producto.imagen:
                # Si se ha cambiado la imagen y existe una imagen antigua
                if producto.imagen.name:
                    # Obtener el public_id de Cloudinary a partir de la URL de la imagen
                    image_url = producto.imagen.url
                    public_id = image_url.split('/v1/media/')[1].split('/')[1].split('.')[0]
                    
                    # Eliminar la imagen en Cloudinary
                    cloudinary.uploader.destroy(public_id, resource_type='image')

            # Guardar los cambios
            form.save()
            # Mensaje de éxito
            messages.success(request, "¡Producto actualizado correctamente!")
            return redirect('administradores')  # Redirigir a la página de administradores o donde corresponda
        else:
            aux['form'] = form
            # Mensaje de error
            messages.error(request, "¡El formulario no es válido!")

    return render(request, 'core/administradores/crud/updateP.html', aux)
@usuario_de_tipo('admin')
def eliminar_producto(request, producto_id):
    producto = Producto.objects.get(pk=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente.')
    return redirect('administradores')
def enable_or_disable_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    frase = ""
    if producto.habilitado:
        producto.habilitado = False
        frase = "deshabilitado"
    else:
        producto.habilitado = True
        frase = "habilitado"
    producto.save()
    
    # Devolver una respuesta JSON con un mensaje y el nuevo estado del producto
    data = {
        'message': f'¡Producto {frase} con éxito!',
        'habilitado': producto.habilitado
    }
    return JsonResponse(data)
@usuario_de_tipo('admin')
def listar_para_administradores(request):
    messages.get_messages(request).used = True
    tipo = get_object_or_404(TipoUsuario, nom_tipo='miembro')
    aux = {
        'artistas': Artista.objects.all().order_by('pk'),
        'productos': Producto.objects.all().order_by('pk'),
        'miembros': Usuario.objects.filter(tipo_usuario=tipo).order_by('pk')
    }
    return render(request, 'core/administradores/crud/list.html', aux)
@usuario_de_tipo('admin')
def agregar_miembro(request):
    storage = messages.get_messages(request)
    storage.used = True
    aux = { 'form': registerForm()
    }
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            tipo = get_object_or_404(TipoUsuario, nom_tipo='miembro')
            user = form.save(commit=False)
            user.tipo_usuario = tipo
            user.save()
            group, created = Group.objects.get_or_create(name='miembro')
            user.groups.add(group)
            user.save()
            messages.success(request, f'Cuenta para el miembro #{user.pk}-{user.username} agregada correctamente!')
            return redirect('administradores')
        else:
            aux['form'] = form
            messages.error(request, 'El form no es valido!')
    return render(request, 'core/administradores/crud/miembros_add.html', aux)
def editar_miembro(request, miembro_id):
    storage = messages.get_messages(request)
    storage.used = True
    miembro = get_object_or_404(Usuario, pk=miembro_id)
    aux = { 'form': MiembroForm(instance=miembro) 
    }
    if request.method == 'POST':
        form = MiembroForm(request.POST, instance=miembro)
        if form.is_valid():
            miembro.set_password(form.cleaned_data['password'])
            try:
                miembro.save()
                messages.success(request, 'Contraseña actualizada correctamente.')
            except Exception as e:
                messages.error(request, 'Contraseña no actualizada. Error: {}'.format(e))
            return redirect('administradores')
        else:
            aux['form'] = form
            messages.error(request, 'El form no es valido!')
            #aux['msj'] = "¡La contraseña no es valida!"
    return render(request, 'core/administradores/crud/updateM.html', aux)
@usuario_de_tipo('admin')
def eliminar_miembro(request, miembro_id):
    storage = messages.get_messages(request)
    storage.used = True
    miembro = get_object_or_404(Usuario, pk=miembro_id)
    try:
        miembro.delete()
    except Exception as e:
        print(e)
        messages.error(request, 'No se pudo eliminar al miembro!')
        return redirect('administradores')
    messages.success(request, '¡Miembro eliminado correctamente!')
    return redirect('administradores')
def enable_or_disable_miembro(request, miembro_id):
    miembro = get_object_or_404(Usuario, pk=miembro_id)
    frase = ""
    if miembro.is_active:
        miembro.is_active = False
        frase = "deshabilitado"
    else:
        miembro.is_active = True
        frase = "habilitado"
    miembro.save()

    # Devolver una respuesta JSON con un mensaje y el nuevo estado del producto
    data = {
        'message': f'¡Miembro {frase} con éxito!',
        'habilitado': miembro.is_active
    }
    return JsonResponse(data)


#HISTORIAL COMPRA
@login_required(login_url='/accounts/login/')
@usuario_de_tipo('comun', 'miembro')
def historialcompra(request):
    compras = historial_compra.objects.filter(usuario=request.user).order_by('-pk')

    # Preparar datos de productos con cantidades para cada compra
    compras_con_productos = []
    for compra in compras:
        productos_con_cantidades = []
        for producto_id, cantidad in compra.cantidades_productos.items():
            producto = compra.productos.get(pk=int(producto_id))  # Obtener el producto por su ID
            productos_con_cantidades.append({
                'producto': producto,
                'cantidad': cantidad
            })
        
        compras_con_productos.append({
            'compra': compra,
            'productos_con_cantidades': productos_con_cantidades
        })

    context = {
        'compras_con_productos': compras_con_productos
    }

    return render(request, 'core/compras.html', context)

def registrar_compra(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Validación de datos
        metodo_pago = data.get('metodo_pago')
        total_clp = data.get('total_clp')
        total_usd = data.get('total_usd')
        productos = data.get('productos')  # Lista de IDs de productos
        cantidades_productos = data.get('cantidades')  # Cantidades de productos

        print(metodo_pago)
        print()
        print(total_clp)
        print()
        print(total_usd)
        print()
        print(productos)
        print()
        print(cantidades_productos)

        if not metodo_pago or not total_clp or not total_usd or not productos or not cantidades_productos:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        try:
            # Creación del historial de compra
            compra = historial_compra.objects.create(
                usuario=request.user,  # Asume que tienes un usuario autenticado
                metodo_pago=metodo_pago,
                total_clp=total_clp,
                total_usd=total_usd,
            )

            # Asignación de productos y cantidades
            for item in cantidades_productos:
                producto_id = item['id']
                cantidad = item['cantidad']
                producto = Producto.objects.get(pk=producto_id)
                compra.productos.add(producto)
                compra.cantidades_productos[str(producto_id)] = cantidad

            compra.save()

            # Respuesta exitosa
            return JsonResponse({'message': 'Compra registrada exitosamente'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Método no permitido para otras solicitudes
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def link_callback(uri, rel):
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    # Check if the uri is a static file
    if uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    # Check if the uri is a media file
    elif uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    else:
        return uri  # Handle the case where the uri doesn't match static or media

    # Check if the file exists
    if not os.path.isfile(path):
        raise Exception('File not found: {}'.format(path))
    
    return path

def generar_voucher(request, compra_id):
    compra = get_object_or_404(historial_compra, id=compra_id, usuario=request.user)
    productos_con_cantidades = []
    for producto_id, cantidad in compra.cantidades_productos.items():
        producto = compra.productos.get(pk=producto_id)
        productos_con_cantidades.append({'producto': producto, 'cantidad': cantidad})
    
    context = {
        'compra': compra,
        'productos_con_cantidades': productos_con_cantidades,
    }

    template_path = 'core/voucherpdf.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="voucher_compra_{compra.pk}.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback
    )

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF: %s' % pisa_status.err, status=500)
    
    return response

#AXES
def locked(request):
    return render(request, 'registration/locked.html')