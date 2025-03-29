from typing import Reversible
import django
from django.db.models.enums import Choices
from django.forms import forms
from django.http import request, JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from core.helpers import campo_valido_sin_numeros
from core.models import Pais, Provincia, Localidad, TipoHabitacion, Servicio, Categoria, Persona, Vendedor, Encargado, Cliente
from hotel.models import Hotel
from venta.services import documento_valido
from .forms import PaisForm, LocalidadForm, AutenticacionForm, ProvinciaForm, TipoHabitacionForm, ServicioForm, CategoriaForm, VendedorForm, EncargadoForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.models import Group, User
from django.utils import timezone
from hotel import views as hviews
from venta import views as vviews
import json

from django.views.generic.edit import CreateView


"""def ingresoAdmin(request):
    # Si estamos identificados devolvemos la portada
    if request.user.is_authenticated:
        return render(request, "administrador.html")
    # En otro caso redireccionamos al login
    return redirect('/home.html')"""


def home(request):
    form = AutenticacionForm()
    if request.method == "POST":
        # Añadimos los datos recibidos al formulario
        form = AuthenticationForm(data=request.POST)
        # Si el formulario es válido...
        if form.is_valid():
            # Recuperamos las credenciales validadas
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Verificamos las credenciales del usuario
            user = authenticate(username=username, password=password)


            # Si existe un usuario con ese nombre y contraseña
            if user is not None:
                # Hacemos el login manualmente
                do_login(request, user)
                usr = User.objects.get(username=user)
                if usr.groups.filter(name='Administrador').exists():
                    return redirect("core:administrador")
                else:
                    # Y le redireccionamos a la portada
                    return redirect("core:vendedor")
            else:
                    mensaje = "Error al iniciar sesion , verifique su usuario y contraseña"
                    return render(request, "home.html", {'form': form , "mensaje_error":mensaje})
        else:
                mensaje = "Error al iniciar sesion , verifique su usuario y contraseña"
                return render(request, "home.html", {'form': form , "mensaje_error":mensaje})

    # Si llegamos al final renderizamos el formulario
    return render(request, "home.html", {'form': form})


def correctaAdmin(request):
    return redirect("hotel:hotel")


def correctaVendedor(request):
    return redirect("venta:vendedor")


def regionAdmin(request):
    personaInstancia = request.user.persona
    paises = Pais.objects.all()
    provincias = Provincia.objects.all()
    localidades = Localidad.objects.all()
    return render(request, "core/regionAdmin.html", {"paises": paises, "localidades": localidades, "provincias": provincias,"administrador":personaInstancia})


def logout(request):
    if request.user.is_authenticated:
        do_logout(request)
    return redirect(home)
     

def localidadCrear(request):
    # tomo todas las localidades (la idea aca es usarlas para controlar entradas)
    localidades = Localidad.objects.all()
    # variable que toma el formulario con datos que se envia
    formLocalidad = LocalidadForm(request.POST)
    if request.method == "POST":  # si se usa el envio ....
        if formLocalidad.is_valid():  # si es valido el formulario ...
            formLocalidad.save()  # se graba!
            return redirect('core:opcionRegion')  # se redirige hacia region
        else:
            formLocalidad = LocalidadForm(data=request.POST)
            erroresDelFormulario = formLocalidad.errors
            return render(request,  "core/modals/modal_localidad_crear.html", {"localidades": localidades, "formulario": formLocalidad , "errores": erroresDelFormulario})
    # si el metodo es GET se renderiza el modal con un formulario vacio
    return render(request, "core/modals/modal_localidad_crear.html", {"localidades": localidades, "formulario": formLocalidad})


def provinciaCrear(request):
    provincias = Provincia.objects.all()
    formProvincia = ProvinciaForm(request.POST)
    if request.method == 'POST':
        if formProvincia.is_valid():
            formProvincia.save()
            return redirect('core:opcionRegion')
        else:
            formProvincia = ProvinciaForm(data=request.POST)
            erroresDelFormulario = formProvincia.errors
            return render(request, "core/modals/modal_provincia_crear.html", {"provincias": provincias , "formulario": formProvincia , "errores": erroresDelFormulario})
    return render(request, "core/modals/modal_provincia_crear.html", {"provincias": provincias, "formulario": formProvincia})


def paisCrear(request):
    paises = Pais.objects.all()
    formPais = PaisForm(data=request.POST)
    if request.method == "POST":
        if formPais.is_valid():
            formPais.save()
            return redirect('core:opcionRegion')  # se redirige a region
        else:
            formPais = PaisForm(data=request.POST)
            erroresDelFormulario = formPais.errors
            return render(request, "core/modals/modal_pais_crear.html", {"paises": paises, "formulario": formPais, "errores": erroresDelFormulario})
    return render(request, "core/modals/modal_pais_crear.html", {"paises": paises, "formulario": formPais})


# se recibe la el objeto ciudad que corresponde a la linea donde se encontraba el boton modificar
def localidadModificar(request, ciudad):
    # ciudadInstancia es el objeto Localidad que corresponde a la ciudad, esto es para modificar lo que ya existe
    ciudadInstancia = get_object_or_404(Localidad, nombre=ciudad)
    # localidades se pretende usar para controlar los ingresos
    localidades = Localidad.objects.all()
    if request.method == 'POST':  # si el metodo es post, esto es el envio de la modificacion
        # el fomulario toma los datos del objeto correspondiente a la ciudad a modificar
        form = LocalidadForm(request.POST, instance=ciudadInstancia)
        if form.is_valid():  # si el formulario es valido
            # tomamos el campo nombre de la instancia que teniamos y la cambiamos por la que nos devuelve el formulario
            ciudadInstancia.nombre = request.POST['nombre']
            ciudadInstancia.save()  # se graba la modificacion
            return redirect('core:opcionRegion')  # se redirige a region
        else:  # si el formulario no fue valido se devuelve para mostrar errores
            form = LocalidadForm(request.POST, instance=ciudadInstancia)
    else:  # si el metodo es GET ...
        form = LocalidadForm(instance=ciudadInstancia)
    return render(request, "core/modals/modal_localidad_modificar.html", {"localidades": localidades, "formulario": form, "ciudad": ciudadInstancia})


def provinciaModificar(request, provincia):
    provinciaInstancia = get_object_or_404(Provincia, nombre=provincia)
    provincias = Provincia.objects.all()
    if request.method == 'POST':
        form = ProvinciaForm(request.POST, instance=provinciaInstancia)
        if form.is_valid():
            provinciaInstancia.nombre = request.POST['nombre']
            provinciaInstancia.save()
            return redirect('core:opcionRegion')
        else:
            form = ProvinciaForm(request.POST, instance=provinciaInstancia)
    else:
        form = ProvinciaForm(instance=provinciaInstancia)
    return render(request, "core/modals/modal_provincia_modificar.html", {"provincias": provincias, "formulario": form, "provincia": provinciaInstancia})


def paisModificar(request, pais):
    paisInstancia = get_object_or_404(Pais, nombre=pais)
    paises = Pais.objects.all()
    if request.method == 'POST':
        form = PaisForm(request.POST, instance=paisInstancia)
        if form.is_valid():
            paisInstancia.nombre = request.POST['nombre']
            paisInstancia.save()
            return redirect('core:opcionRegion')
        else:
            form = PaisForm(request.POST, instance=paisInstancia)
    else:
        form = PaisForm(instance=paisInstancia)
    return render(request, "core/modals/modal_pais_modificar.html", {"paises": paises, "formulario": form, "pais": paisInstancia})


# GESTION TIPO HABITACION


def tipoHabitacion(request):
    personaInstancia = request.user.persona
    tiposHabitaciones = TipoHabitacion.objects.all()
    return render(request, "core/tipoHabitacionAdmin.html", {"tiposHabitaciones": tiposHabitaciones,"administrador":personaInstancia})

def tipoHabitacionCrear(request):
    coltiposHabitaciones = TipoHabitacion.objects.all()
    formTipoHabitacion = TipoHabitacionForm(request.POST)
    if request.method == 'POST':
        if formTipoHabitacion.is_valid():
            formTipoHabitacion.save()
            return redirect('core:opcionTipoHabitacion')
    return render(request, "core/modals/modal_tipoHabitacion_crear.html", {"coltiposHabitaciones": coltiposHabitaciones, "formulario": formTipoHabitacion})


def tipoHabitacionModificar(request, tipoHabitacion):
    tipoHabitacionInstancia = get_object_or_404(
        TipoHabitacion, nombre=tipoHabitacion)
    coltiposHabitaciones = TipoHabitacion.objects.all()
    if request.method == 'POST':
        form = TipoHabitacionForm(
            request.POST, instance=tipoHabitacionInstancia)
        if form.is_valid():
            tipoHabitacionInstancia.nombre = request.POST['nombre']
            tipoHabitacionInstancia.descripcion = request.POST['descripcion']
            tipoHabitacionInstancia.pasajeros = request.POST['pasajeros']
            tipoHabitacionInstancia.cuartos = request.POST['cuartos']
            tipoHabitacionInstancia.save()
            return redirect('core:opcionTipoHabitacion')
        else:
            form = TipoHabitacionForm(
                request.POST, instance=tipoHabitacionInstancia)
    else:
        form = TipoHabitacionForm(instance=tipoHabitacionInstancia)
    return render(request, "core/modals/modal_tipoHabitacion_modificar.html", {"coltiposHabitaciones": coltiposHabitaciones, "formulario": form, "tipoHabitacion": tipoHabitacionInstancia})


# GESTION SERVICIOS


def servicio(request):
    personaInstancia = request.user.persona
    colServicios = Servicio.objects.all()
    return render(request, "core/servicioAdmin.html", {"colServicios": colServicios,"administrador":personaInstancia})


def servicioCrear(request):
    colServicios = Servicio.objects.all()
    form = ServicioForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('core:servicio')
    return render(request, "core/modals/modal_servicio_crear.html", {"colServicios": colServicios, "formulario": form})


def serviciosModificar(request, servicio):
    servicioInstancia = get_object_or_404(Servicio, nombre=servicio)
    colServicios = Servicio.objects.all()
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicioInstancia)
        if form.is_valid():
            servicioInstancia.nombre = request.POST['nombre']
            servicioInstancia.descripcion = request.POST['descripcion']
            servicioInstancia.save()
            return redirect('core:servicio')
        else:
            form = ServicioForm(request.POST, instance=servicioInstancia)
    else:
        form = ServicioForm(instance=servicioInstancia)
    return render(request, "core/modals/modal_servicio_modificar.html", {"colServicios": colServicios, "formulario": form, "servicio": servicioInstancia})

# GESTION CATEGORIAS


def categoria(request):
    personaInstancia = request.user.persona
    colCategorias = Categoria.objects.all()
    return render(request, "core/categoriaAdmin.html", {"colCategorias": colCategorias,"administrador":personaInstancia})


def categoriaCrear(request):
    colCategorias = Categoria.objects.all()
    form = CategoriaForm(request.POST)
    if request.method == "POST":
        nueva_categoria = request.POST["nombre"]
        nombre_campo = "nombre"
        if campo_valido_sin_numeros(nueva_categoria , form , nombre_campo ):
            if form.is_valid():
                form.save()
                return redirect('core:categoria')
    return render(request, "core/modals/modal_categoria_crear.html", {"colCategorias": colCategorias, "formulario": form})


def categoriaModificar(request, categoria):
    categoriaInstancia = get_object_or_404(Categoria, nombre=categoria)
    colCategorias = Categoria.objects.all()
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoriaInstancia)
        if form.is_valid():
            categoriaInstancia = form.save(commit=False)
            categoriaInstancia.nombre = request.POST['nombre']
            categoriaInstancia.estrellas = request.POST['estrellas']
            categoriaInstancia.save()
            form.save_m2m()
            return redirect('core:categoria')
        else:
            form = CategoriaForm(request.POST, instance=categoriaInstancia)
    else:
        form = CategoriaForm(instance=categoriaInstancia)
        form.fields['nombre'].widget.attrs['readonly'] = True
        form.fields['estrellas'].widget.attrs['style'] = 'display:none;'
        form.fields['estrellas'].label = ''
        form.fields['servicios'].choices = [
            (c.pk, c.nombre) for c in Servicio.objects.all()]
        arregloTildados = categoriaInstancia.servicios.all()
        preseleccion = []
        for servicio in arregloTildados:
            preseleccion.append(servicio.pk)
        form.initial['servicios'] = preseleccion

    return render(request, "core/modals/modal_categoria_modificar.html", {"colCategorias": colCategorias, "formulario": form, "categoria": categoriaInstancia})

# GESTION VENDEDOR


def vendedores(request):
    personaInstancia = request.user.persona
    colVendedores = Vendedor.objects.all()
    colEncargados = Encargado.objects.all()
    return render(request, "core/vendedor.html", {"colVendedores": colVendedores, "colEncargados": colEncargados,"administrador":personaInstancia})


def vendedorCrear(request):
    colVendedores = Vendedor.objects.all()
    form = VendedorForm(request.POST, request.FILES)  # Asegúrate de incluir request.FILES
    if request.method == "POST":
        dni_nuevo_cliente = request.POST['documento']
        if documento_valido(dni_nuevo_cliente, form):
            if form.is_valid():
                if 'imagen' in request.FILES:
                    imagen = request.FILES['imagen']
                form.imagen = imagen 
                form.save()
                form.instance.hacer_vendedor(
                    form.cleaned_data['usuario'], form.cleaned_data['email'], form.cleaned_data['contrasenia'])
                return redirect('core:opcionVendedor')
    return render(request, "core/modals/modal_vendedor_crear.html", {"colVendedores": colVendedores, "formulario": form})


def vendedorModificar(request, vendedor):
    vendedorInstancia = get_object_or_404(Vendedor, pk=vendedor)
    colVendedores = Vendedor.objects.all()
    if request.method == 'POST':
        form = VendedorForm(request.POST, instance=vendedorInstancia)
        if form.is_valid():

            vendedorInstancia.persona.nombre = request.POST['nombre']
            vendedorInstancia.persona.apellido = request.POST['apellido']
            vendedorInstancia.persona.documento = request.POST['documento']
            vendedorInstancia.persona.tipo_documento = request.POST['tipo_documento']
            vendedorInstancia.persona.usuario.email = request.POST['email']
            vendedorInstancia.persona.usuario.username = request.POST['usuario']
            vendedorInstancia.persona.usuario.password = request.POST['contrasenia']

            vendedorInstancia.persona.usuario.save()
            vendedorInstancia.persona.save()
            vendedorInstancia.save()
            return redirect('core:opcionVendedor')
        else:
            form = VendedorForm(request.POST, instance=vendedorInstancia)
    else:
        form = VendedorForm(instance=vendedorInstancia)
        form.fields["nombre"].initial = vendedorInstancia.persona.nombre
        form.fields["apellido"].initial = vendedorInstancia.persona.apellido
        form.fields["documento"].initial = vendedorInstancia.persona.documento
        form.fields["tipo_documento"].initial = vendedorInstancia.persona.tipo_documento
        form.fields["email"].initial = vendedorInstancia.persona.usuario.email
        form.fields["usuario"].initial = vendedorInstancia.persona.usuario.username
        form.fields["contrasenia"].initial = vendedorInstancia.persona.usuario.password
    return render(request, "core/modals/modal_vendedor_modificar.html", {"colVendedores": colVendedores, "formulario": form, "vendedor": vendedorInstancia})


def vendedorEliminar(request, vendedor):
    vendedorInstancia = get_object_or_404(Vendedor, pk=vendedor)
    if request.method == "POST":
        vendedorInstancia.set_baja()
        colHoteles = Hotel.objects.filter(vendedores=vendedorInstancia.pk)
        for hotel in colHoteles:
            hotel.vendedores.remove(vendedorInstancia)
            hotel.save()
        return redirect('core:opcionVendedor')
    return render(request, "core/modals/modal_vendedor_eliminar.html", {"vendedor": vendedorInstancia})


def vendedorReciclar(request, vendedor):
    vendedorInstancia = get_object_or_404(Vendedor, pk=vendedor)
    if request.method == "POST":
        vendedorInstancia.dar_alta()
        vendedorInstancia.save()
        return redirect('core:opcionVendedor')
    return render(request, "core/modals/modal_vendedor_reciclar.html", {"vendedor": vendedorInstancia})

#                    GESTION ENCARGADO


def encargadoCrear(request):
    colEncargados = Encargado.objects.all()
    form = EncargadoForm(request.POST)
    if request.method == "POST":
        dni_nuevo_cliente = request.POST['documento']
        if documento_valido(dni_nuevo_cliente , form):
            if form.is_valid():
                form.save()
                form.instance.hacer_encargado(form.cleaned_data['clave'])
                form.save()
                return redirect('core:opcionVendedor')
    return render(request, "core/modals/modal_encargado_crear.html", {"colEncargados": colEncargados, "formulario": form})


def encargadoModificar(request, encargado):
    encargadoInstancia = get_object_or_404(Encargado, pk=encargado)
    colEncargados = Encargado.objects.all()
    if request.method == 'POST':
        form = EncargadoForm(request.POST, instance=encargadoInstancia)
        if form.is_valid():

            encargadoInstancia.persona.nombre = request.POST['nombre']
            encargadoInstancia.persona.apellido = request.POST['apellido']
            encargadoInstancia.persona.documento = request.POST['documento']
            encargadoInstancia.persona.tipo_documento = request.POST['tipo_documento']
            encargadoInstancia.clave = request.POST['clave']

            encargadoInstancia.persona.save()
            encargadoInstancia.save()
            return redirect('core:opcionVendedor')
        else:
            form = EncargadoForm(request.POST, instance=encargadoInstancia)
    else:
        form = EncargadoForm(instance=encargadoInstancia)
        form.fields["nombre"].initial = encargadoInstancia.persona.nombre
        form.fields["apellido"].initial = encargadoInstancia.persona.apellido
        form.fields["documento"].initial = encargadoInstancia.persona.documento
        form.fields["tipo_documento"].initial = encargadoInstancia.persona.tipo_documento
        form.fields["clave"].initial = encargadoInstancia.clave
    return render(request, "core/modals/modal_encargado_modificar.html", {"colEncargados": colEncargados, "formulario": form, "encargado": encargadoInstancia})


def encargadoEliminar(request, encargado):
    encargadoInstancia = get_object_or_404(Encargado, pk=encargado)
    if request.method == "POST":
        encargadoInstancia.set_baja()
        encargadoInstancia.save()
        return redirect('core:opcionVendedor')
    return render(request, "core/modals/modal_encargado_eliminar.html", {"encargado": encargadoInstancia})


def encargadoReciclar(request, encargado):
    encargadoInstancia = get_object_or_404(Encargado, pk=encargado)
    if request.method == "POST":
        encargadoInstancia.dar_alta()
        encargadoInstancia.save()
        return redirect('core:opcionVendedor')
    return render(request, "core/modals/modal_encargado_reciclar.html", {"encargado": encargadoInstancia})

# GESTION CLIENTE


def cliente(request):
    personaInstancia = request.user.persona
    colClientes = Cliente.objects.all()
    return render(request, "core/clienteAdmin.html", {"colClientes": colClientes,"administrador":personaInstancia})


def clienteEliminar(request, cliente):
    clienteInstancia = get_object_or_404(Cliente, pk=cliente)
    if request.method == "POST":
        clienteInstancia.set_baja()
        clienteInstancia.save()
        return redirect('core:cliente')
    return render(request, "core/modals/modal_cliente_eliminar.html", {"cliente": clienteInstancia})


def clienteReciclar(request, cliente):
    clienteInstancia = get_object_or_404(Cliente, pk=cliente)
    if request.method == "POST":
        clienteInstancia.dar_alta()
        clienteInstancia.save()
        return redirect('core:cliente')
    return render(request, "core/modals/modal_cliente_reciclar.html", {"cliente": clienteInstancia})


