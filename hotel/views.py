from datetime import date, datetime
import json
from django.contrib.auth.decorators import login_required
from django.db.models import fields
from django.db.models.fields import DateField
from django.forms.widgets import DateInput
from django.shortcuts import render
from typing import Reversible
import django
from django.forms import forms
from django.http import request, JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from hotel.helpers import habitacion_duplicada, hay_fechas_superpuestas
from hotel.models import Habitacion, Hotel, PrecioPorTipo, TemporadaAlta, PaqueteTuristico
from venta.models import Factura
from .forms import  HabitacionForm, HotelForm, ServicioForm, TemporadaHotelForm, AgregarTipoAHotelForm, HabitacionForm, PaqueteTuristicoForm, VendedorHotelForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as do_login
from django.contrib.auth import logout
from django.contrib.auth.models import Group, User
from django.utils import timezone
from django.views.generic.edit import CreateView
from core.models import Persona, Vendedor, Categoria, TipoHabitacion, Servicio
from collections import defaultdict


# Create your views here.
@login_required
def hotel(request):
    personaInstancia = request.user.persona
    colHoteles=Hotel.objects.all()
    return render(request, "hotel/hotelAdmin.html",{"colHoteles": colHoteles, "administrador":personaInstancia})

def hotelCrear(request):
    colHoteles = Hotel.objects.all()
    
    # Solo se debe instanciar el formulario con POST y FILES si el método es POST
    if request.method == "POST":
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardamos la instancia del hotel
            hotelInstancia = form.save()

            # Si se sube una imagen, se puede mostrar el nombre del archivo
            if 'imagen' in request.FILES:
                imagen = request.FILES['imagen']
                print("Imagen cargada:", imagen.name)  # Muestra el nombre del archivo de la imagen
            
            # Añadimos los servicios de la categoría del hotel
            for servicio in hotelInstancia.categoria.servicios.all():
                hotelInstancia.servicios.add(servicio)
            
            hotelInstancia.save()
            return redirect('hotel:hotel')  # Redirigir a la vista deseada
    else:
        form = HotelForm()  # Si no es POST, creamos un formulario vacío
    
    return render(request, "hotel/modals/modal_hotel_crear.html", {
        "colHoteles": colHoteles,
        "formulario": form
    })
    
def hotelModificar(request, hotel):
    hotelInstancia = get_object_or_404(Hotel, pk= hotel )
    colHoteles = Hotel.objects.all()
    if request.method == 'POST':
        form=HotelForm(request.POST,instance=hotelInstancia)
        if form.is_valid():
            hotelInstancia = form.save()
            hotelInstancia.nombre=request.POST['nombre']
            hotelInstancia.direccion=request.POST['direccion']
            hotelInstancia.email=request.POST['email']
            categoria = get_object_or_404( Categoria , pk=request.POST['categoria'])
            hotelInstancia.imagen="static/media/hoteles/"+request.POST['imagen']
            
            hotelInstancia.categoria=categoria
            for servicio in hotelInstancia.categoria.servicios.all():
                    hotelInstancia.servicios.add(servicio)
            #hotelInstancia.localidad=request.POST['localidad']
            hotelInstancia.save()
            #form.save_m2m()
            return redirect('hotel:hotel')
        else:
            form=HotelForm(request.POST,instance=hotelInstancia)
    else:
        form=HotelForm(instance=hotelInstancia)
        form.fields['nombre'].widget.attrs['readonly'] = True
        form.fields['localidad'].widget.attrs['style'] = 'display:none;'
        form.fields['localidad'].label = ''
        form.fields['direccion'].widget.attrs['readonly'] = True
        form.fields['encargado'].widget.attrs['style'] = 'display:none;'
        form.fields['encargado'].label = ''
        """
        form.fields['direccion'].widget.attrs['readonly'] = True
        form.fields['encargado'].widget.attrs['readonly'] = True
        """
    return render(request, "hotel/modals/modal_hotel_modificar.html", {"colHoteles": colHoteles, "formulario": form, "hotel": hotelInstancia})


def detalleHotel(request,hotel):
    personaInstancia = request.user.persona
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)  
    return render(request, "hotel/vistaHotelAdmin.html",{"hotel":hotelInstancia,"administrador":personaInstancia})


#-------------------------- INICIO: TIPO DE HABITACION ----------------------------------------

def vistaTipoHabitacionHotel(request,hotel):
    personaInstancia = request.user.persona
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    tarifas_hotel=hotelInstancia.tarifario.all()
    return render(request, "hotel/tipoHabitacion_Hotel_Admin.html",{"hotel":hotelInstancia, "tarifas":tarifas_hotel,"administrador":personaInstancia })




def tipoHabitacionCrear(request, hotel):
    hotelInstancia = get_object_or_404(Hotel, pk=hotel)

    if request.method == "POST":
        formulario = AgregarTipoAHotelForm(request.POST)

        if formulario.is_valid():
            precioBaja = formulario.cleaned_data["baja"]
            precioAlta = formulario.cleaned_data["alta"]

            if precioBaja >= 0 and precioAlta >= 0:
                tipoHabitacionRecibido = formulario.save(commit=False)
                tipoHabitacionRecibido.hotel = hotelInstancia
                tipoHabitacionRecibido.save()
                return redirect('hotel:tipoHabitacionHotel', hotel)
        else:
            return render(request, "hotel/modals/modal_tipoHabitacionHotel_crear.html", {
                "hotel": hotelInstancia,
                "formulario": formulario,
                "errores": formulario.errors
            })
    else:
        formulario = AgregarTipoAHotelForm()

    return render(request, "hotel/modals/modal_tipoHabitacionHotel_crear.html", {
        "hotel": hotelInstancia,
        "formulario": formulario
    })


def tipoHabitacionModificar(request,hotel,tipo):
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    tipoHabitacionInstancia=get_object_or_404(PrecioPorTipo,pk=tipo)
    if request.method == 'POST':
        formulario=AgregarTipoAHotelForm(request.POST,instance=tipoHabitacionInstancia)
        if formulario.is_valid():
            tipoHabitacionInstancia = formulario.save()
            tipoHabitacionInstancia.alta=request.POST['alta']
            tipoHabitacionInstancia.baja=request.POST['baja']
            tipoHabitacionInstancia.save()
            return redirect('hotel:tipoHabitacionHotel', hotel)
        else:
            formulario=AgregarTipoAHotelForm(request.POST,instance=tipoHabitacionInstancia)
    else:
        formulario=AgregarTipoAHotelForm(instance=tipoHabitacionInstancia)
        formulario.fields['tipo'].widget.attrs['style'] = 'display:none;'
        formulario.fields['tipo'].label = ''
    return render(request, "hotel/modals/modal_tipoHabitacionHotel_modificar.html",{"formulario":formulario, "hotel":hotelInstancia ,"tipo":tipoHabitacionInstancia})


def tipoHabitacionEliminar(request, hotel, tipo): 
    hotelInstancia = get_object_or_404(Hotel, pk=hotel)
    tipoHabitacionInstancia = get_object_or_404(PrecioPorTipo, pk=tipo)
    if request.method == 'POST':
        # 1. Buscar todas las habitaciones de este hotel con este tipo
        habitaciones_a_eliminar = Habitacion.objects.filter(hotel=hotelInstancia, tipo=tipoHabitacionInstancia.tipo)
        # 2. Buscar y eliminar paquetes turísticos que incluyan alguna de estas habitaciones
        from hotel.models import PaqueteTuristico
        paquetes_a_eliminar = PaqueteTuristico.objects.filter(
            hotel=hotelInstancia, habitaciones__in=habitaciones_a_eliminar
        ).distinct()
        for paquete in paquetes_a_eliminar:
            paquete.delete()
        # 3. Eliminar las habitaciones y el tipo de habitación
        habitaciones_a_eliminar.delete()
        tipoHabitacionInstancia.delete()
        return redirect('hotel:tipoHabitacionHotel', hotel)
    return render(request, "hotel/modals/modal_tipoHabitacionHotel_eliminar.html", {
        "hotel": hotelInstancia,
        "tipo": tipoHabitacionInstancia
    })
    



#-------------------------- FIN TIPO DE HABITACION ----------------------------------------




#-------------------------- GESTION HABITACIONES ----------------------------------------

def habitacionCrear(request,hotel):
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    formulario=HabitacionForm(request.POST)
    if request.method == "POST":
        numero_habitacion_nuevo = request.POST["numero"]
        if formulario.is_valid():
            if not (habitacion_duplicada(numero_habitacion_nuevo , hotel ,formulario)):
                habitacionInstancia=formulario.save(commit=False)
                habitacionInstancia.hotel= hotelInstancia
                habitacionInstancia.save()
                return redirect('hotel:vistaHotel',hotel)
    else:
        formulario=HabitacionForm(request.GET)
        formulario.fields['tipo'].choices=[(t.pk,t.nombre) for t in hotelInstancia.get_tipos()]

    return render(request, "hotel/modals/modal_habitacionHotel_crear.html",{"hotel":hotelInstancia,'formulario':formulario })


def habitacionEliminar(request,hotel,habitacion):
    hotelInstancia = get_object_or_404(Hotel, pk=hotel)
    habitacionInstancia = get_object_or_404(Habitacion, pk=habitacion)
    if request.method == "POST":
        # Buscar y eliminar paquetes turísticos que incluyan esta habitación
        from hotel.models import PaqueteTuristico
        paquetes_a_eliminar = PaqueteTuristico.objects.filter(
            hotel=hotelInstancia, habitaciones=habitacionInstancia
        ).distinct()
        for paquete in paquetes_a_eliminar:
            paquete.delete()
        habitacionInstancia.dar_baja()
        habitacionInstancia.save()
        return redirect('hotel:vistaHotel', hotel)
    return render(request, "hotel/modals/modal_habitacionHotel_eliminar.html", {"hotel": hotelInstancia, 'habitacion': habitacionInstancia })

def habitacionReciclar(request,hotel,habitacion):
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    habitacionInstancia=get_object_or_404(Habitacion,pk=habitacion)
    if request.method == "POST":
        habitacionInstancia.dar_alta()
        habitacionInstancia.save()
        return redirect('hotel:vistaHotel',hotel)
    return render(request, "hotel/modals/modal_habitacionHotel_reciclar.html",{"hotel":hotelInstancia,'habitacion':habitacionInstancia })

#-------------------------- GESTION HABITACIONES ----------------------------------------




#-------------------------- INICIO: GESTION TEMPORADAS ----------------------------------------

def temporadaHotel(request,hotel):
    personaInstancia = request.user.persona
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)    
    return render(request, "hotel/temporada_Hotel_Admin.html",{"hotel":hotelInstancia,"administrador":personaInstancia })


def temporadaHotelCrear(request, hotel):
    form = TemporadaHotelForm(request.POST)
    hotelInstancia=get_object_or_404(Hotel, pk=hotel)
    if request.method == "POST":
            form = TemporadaHotelForm(request.POST)
            temporadas = TemporadaAlta.objects.filter(hotel = hotel )
            fecha_inicio = request.POST["inicio"]
            fecha_fin = request.POST["fin"]
            for temporada in  temporadas:
                if (hay_fechas_superpuestas(fecha_inicio ,fecha_fin , str(temporada.inicio), str(temporada.fin))):
                    form.add_error('inicio', 'las fechas se superponen con alguna existentes')
                    return render(request, "hotel/modals/modal_temporadaHotel_crear.html", { "hotel": hotelInstancia, "formulario": form})
            if form.is_valid():
                form = TemporadaHotelForm(request.POST)
                temporadaInstancia=form.save(commit=False)
                temporadaInstancia.hotel= hotelInstancia
                temporadaInstancia.save()
                return redirect('hotel:temporadaHotel', hotel)
    return render(request, "hotel/modals/modal_temporadaHotel_crear.html", { "hotel": hotelInstancia, "formulario": form})

def temporadaEliminar(request,hotel,temporada):
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    temporadaInstancia=get_object_or_404(TemporadaAlta,pk=temporada)
    if request.method == "POST":
        temporadaInstancia.delete()
        
        return redirect('hotel:temporadaHotel',hotel)
    return render(request, "hotel/modals/modal_temporadaHotel_eliminar.html",{"hotel":hotelInstancia,'temporada':temporadaInstancia })


def temporadaModificar(request,hotel,temporada):
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    temporadaInstancia=get_object_or_404(TemporadaAlta,pk=temporada)
    form = TemporadaHotelForm(request.POST or None,instance=temporadaInstancia)
    if request.method=="POST":
        if form.is_valid():
            temporada=form.save(commit=False)
            temporada.save()
            return redirect('hotel:temporadaHotel',hotel)
    else:
        form.initial['inicio']=str(temporadaInstancia.inicio)
        form.initial['fin']=str(temporadaInstancia.fin)
    return render(request, "hotel/modals/modal_temporadaHotel_modificar.html",{"formulario":form,"hotel":hotelInstancia,'temporada':temporadaInstancia })

#-------------------------- FIN: GESTION TEMPORADAS ----------------------------------------

#-------------------------- INICIO: GESTION PAQUETES TURISTICOS ----------------------------------------

def paqueteTuristicoHotel(request,hotel):
    personaInstancia = request.user.persona
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)    
    return render(request, "hotel/vistaHotelAdmin.html",{"hotel":hotelInstancia,"administrador":personaInstancia })
    

def paqueteTuristicoHotelCrear(request, hotel):
    id_hotel = hotel
    form = PaqueteTuristicoForm(request.POST)
    hotel_actual = get_object_or_404(Hotel, pk=id_hotel)
    if request.method == "POST":
        fecha_inicio = request.POST['inicio']
        fecha_fin = request.POST['fin']
        if (fecha_inicio == fecha_fin):
            form.add_error('inicio', 'la fecha inicio no puede ser igual a la fecha de finalizacion')
            form.add_error('fin', 'la fecha finalizacion no puede ser igual a la fecha de inicio')
            return render(request, "hotel/modals/modal_paqueteTuristicoHotel_crear.html", { "hotel": hotel_actual, "formulario": form})       
        id_habitaciones = request.POST.getlist('habitaciones')
        for id_habitacion in id_habitaciones:
            habitacion = Habitacion.objects.get(id=id_habitacion)
            # Verificar si la habitación está dada de baja
            if habitacion.baja:
                form.fields['habitaciones'].choices = [(c.pk, c.numero) for c in Habitacion.objects.filter(hotel=hotel_actual)]
                form.add_error('habitaciones', f'La habitación {habitacion.numero} está dada de baja y no puede ser seleccionada.')
                return render(request, "hotel/modals/modal_paqueteTuristicoHotel_crear.html", { "hotel": hotel_actual, "formulario": form})
            paquetes = habitacion.paqueteturistico.all()
            for paquete in paquetes:
                if (hay_fechas_superpuestas(fecha_inicio, fecha_fin, str(paquete.inicio), str(paquete.fin))):
                    form.fields['habitaciones'].choices = [(c.pk, c.numero) for c in Habitacion.objects.filter(hotel=hotel_actual)]
                    form.add_error('habitaciones', 'alguna de las habitaciones seleccionadas ya tienen un paquete para ese periodo de fechas')
                    return render(request, "hotel/modals/modal_paqueteTuristicoHotel_crear.html", { "hotel": hotel_actual, "formulario": form})        

        # Crear un nuevo objeto PaqueteTuristico
        nuevo_paquete = PaqueteTuristico.objects.create(
            nombre=request.POST['nombre'],
            coeficiente=request.POST['coeficiente'],
            hotel=hotel_actual,
            inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
            fin=datetime.strptime(fecha_fin, '%Y-%m-%d').date(),
            vendido=False,
            precio=1
        )

        # Agregar las habitaciones seleccionadas al nuevo paquete
        for id_habitacion in id_habitaciones:
            habitacion = Habitacion.objects.get(id=id_habitacion)
            nuevo_paquete.habitaciones.add(habitacion)
        return redirect('hotel:paqueteTuristicoHotel', id_hotel)
    form.fields['habitaciones'].choices = [(c.pk, c.numero) for c in Habitacion.objects.filter(hotel=hotel_actual)]
    return render(request, "hotel/modals/modal_paqueteTuristicoHotel_crear.html", { "hotel": hotel_actual, "formulario": form })


def paqueteTuristicoHotelModificar(request,hotel,paquete):
    id_hotel = hotel
    hotelInstancia=get_object_or_404(Hotel, pk=id_hotel)
    paqueteInstancia=get_object_or_404(PaqueteTuristico, pk=paquete)
    form = PaqueteTuristicoForm(request.POST or None,instance=paqueteInstancia)
    if request.method == "POST":
        fecha_inicio = request.POST['inicio']
        fecha_fin = request.POST['fin']
        lista_habitaciones_seleccion = request.POST.getlist('habitaciones')
        lista_filtrada_habitaciones=[]
        for elemento in lista_habitaciones_seleccion:
            habitacion = Habitacion.objects.get(id = elemento)
            lista_filtrada_habitaciones.append(habitacion)
            paquetes = list(habitacion.paqueteturistico.all())
            for x in paquetes:
                if(x.id == paquete):
                    paquetes.remove(x)
            for paq in paquetes:
                if (hay_fechas_superpuestas(fecha_inicio ,fecha_fin , str(paq.inicio), str(paq.fin))):  
                    form.add_error('habitaciones', 'alguna de las habitaciones seleccionadas ya tienen un paquete para ese periodo de fechas')
                    form.fields['habitaciones'].choices=[(c.pk,c.numero) for c in Habitacion.objects.filter(hotel=hotelInstancia)]
                    return render(request, "hotel/modals/modal_paqueteTuristicoHotel_modificar.html",{'formulario':form,'hotel':hotelInstancia,'paquete':paqueteInstancia})

            form.fields['habitaciones'].choices=[(c.pk,c.numero) for c in Habitacion.objects.filter(hotel=hotelInstancia)]
            
        if form.is_valid():
            paqueteInstancia.nombre = request.POST["nombre"]
            paqueteInstancia.coeficiente = request.POST["coeficiente"]
            paqueteInstancia.inicio = request.POST["inicio"]
            paqueteInstancia.fin = request.POST["fin"]
            paqueteInstancia.habitaciones.set(lista_habitaciones_seleccion)
            paqueteInstancia.save()
            return redirect('hotel:paqueteTuristicoHotel', hotel)
    else:
        form.initial['inicio']=str(paqueteInstancia.inicio)
        form.initial['fin']=str(paqueteInstancia.fin)
        dicc={'nombre','habitaciones','inicio','fin'}
        for campo in dicc:
            form.fields[campo].widget.attrs['style'] = ''
            form.fields[campo].label = ''
        form.fields['nombre'].label='nombre'
        form.fields['inicio'].label='inicio'
        form.fields['fin'].label='fin'
        form.fields['habitaciones'].label='Habitaciones'
    form.fields['habitaciones'].choices=[(c.pk,c.numero) for c in Habitacion.objects.filter(hotel=hotelInstancia)]
    return render(request, "hotel/modals/modal_paqueteTuristicoHotel_modificar.html",{'formulario':form,'hotel':hotelInstancia,'paquete':paqueteInstancia})

def paqueteTuristicoHotelEliminar(request,hotel,paquete):
    hotelInstancia=get_object_or_404(Hotel, pk=hotel)
    paqueteInstancia=get_object_or_404(PaqueteTuristico, pk=paquete)
    if request.method=='POST':
        paqueteInstancia.delete()
        return redirect('hotel:paqueteTuristicoHotel', hotel)
    return render(request, "hotel/modals/modal_paqueteTuristicoHotelEliminar.html",{'hotel':hotelInstancia,'paquete':paqueteInstancia})


#-------------------------- FIN: GESTION PAQUETES TURISTICOS ----------------------------------------

#-------------------------- INICIO: GESTION PAQUETES TURISTICOS ----------------------------------------

def serviciosHotel(request,hotel):
    personaInstancia = request.user.persona
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    categoria=hotelInstancia.get_categoria()
    return render(request, "hotel/servicios_Hotel_Admin.html",{"hotel":hotelInstancia,"categoria":categoria,"administrador":personaInstancia})

def aniadirServicioHotel(request,hotel):
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    categoria=hotelInstancia.get_categoria()
    form=ServicioForm(request.POST or None)
    if request.method =="POST":
        diccionario=(dict(request.POST))
        for servicio in diccionario['servicio']:
            hotelInstancia.servicios.add(get_object_or_404(Servicio,pk=servicio))
        hotelInstancia.save()
        return redirect('hotel:serviciosHotel', hotel)
        
    else:
        listaDeServicios=[]
        for servicio in Servicio.objects.all():
            if servicio not in hotelInstancia.get_servicios():
                listaDeServicios.append(get_object_or_404(Servicio, pk=servicio.pk))
        form.fields['servicio'].choices=[(c.pk,c.nombre) for c in listaDeServicios]
        return render(request, "hotel/modals/modal_servicio_Hotel_aniadir.html",{"formulario":form,"hotel":hotelInstancia,"categoria":categoria})
    

#-------------------------- INICIO: GESTION VENDEDORES HOTEL ----------------------------------------
def vendedoresHotel(request,hotel):
    personaInstancia = request.user.persona
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    colVendedores = hotelInstancia.get_vendedores()
   
    return render(request, "hotel/vendedores_Hotel_Admin.html",{"hotel":hotelInstancia,"colVendedores":colVendedores,"administrador":personaInstancia})

def aniadirVendedorHotel(request, hotel):
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    colVendedores = hotelInstancia.get_vendedores()
    
    if request.method =="POST":
        diccionario=(dict(request.POST))
        hotelInstancia.vendedores.add(get_object_or_404(Vendedor,pk=diccionario['vendedores'][0]))
        hotelInstancia.save()
        return redirect('hotel:vendedoresHotel', hotel)
    else:
        vendedoresNoVinculados = []
        for vendedor in Vendedor.objects.all():
            if  vendedor not in colVendedores:
                vendedoresNoVinculados.append(vendedor)

        form = VendedorHotelForm(vendedoresNoVinculados,hotel)
        form.initial['vendedores'] = vendedoresNoVinculados
        return render(request, "hotel/modals/modal_vendedor_Hotel_aniadir.html",{"form": form,"hotel":hotelInstancia, "colVendedores": vendedoresNoVinculados})

def vendedorHotelEliminar(request,hotel,vendedor):
    hotelInstancia=get_object_or_404(Hotel, pk=hotel)
    vendedorInstancia=get_object_or_404(Vendedor, pk=vendedor)
    if request.method=='POST':
        hotelInstancia.vendedores.remove(vendedorInstancia)
        hotelInstancia.save()
        return redirect('hotel:vendedoresHotel', hotel)
    return render(request, "hotel/modals/modal_vendedor_hotel_eliminar.html",{'hotel':hotelInstancia,'vendedor':vendedorInstancia})

def eliminarServicioHotel(request,hotel,servicio):
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    servicioInstancia=get_object_or_404(Servicio,pk=servicio)
    if request.method== "POST":
        hotelInstancia.servicios.remove(servicioInstancia)
        return redirect('hotel:serviciosHotel', hotel)
    return render(request, "hotel/modals/modal_servicio_Hotel_eliminar.html",{"hotel":hotelInstancia,"servicio":servicioInstancia})


def vistaVentasHotel(request, hotel):
    if 'ventas_mes' in request.session:
        return ventasHotelPorMes(request, hotel)
    else:
        return ventasHotelPorDia(request, hotel)
    
    
def limpiar_preferencias_ventas_dias(request,hotel):
    if 'fecha_inicio_ventas-dias' in request.session:
        del request.session['fecha_inicio_ventas-dias']
    if 'fecha_fin_ventas-dias' in request.session:
        del request.session['fecha_fin_ventas-dias']
    return redirect("hotel:ventasHotelPorDia",hotel)

# ventas del hotel por dia total
def ventasHotelPorDia(request, hotel):
    if 'ventas_mes' in request.session:
        del request.session['ventas_mes']
    ventasDias="ventas-dias"
    personaInstancia = request.user.persona
    hotelInstancia = get_object_or_404(Hotel, pk=hotel)
    
    
    if request.method == "POST":
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        request.session['fecha_inicio_ventas-dias']=fecha_inicio
        request.session['fecha_fin_ventas-dias']=fecha_fin
        # Convertir las fechas de inicio y fin a objetos datetime
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        request.session['ventas_dias']= "ventas_dias"

        colHabitaciones = hotelInstancia.get_habitaciones()
        
        ventas = []
        fechas = []
        totales = []
        
        ventas_por_fecha = defaultdict(float)  # Diccionario para acumular las ventas por fecha
        
        for habitacion in colHabitaciones:
            alquileres = habitacion.alquileres.all()
            for alquiler in alquileres:
                factura = Factura.objects.get(id=alquiler.factura_id)
                fecha = factura.fecha.strftime('%Y-%m-%d')
                fecha = datetime.strptime(fecha, '%Y-%m-%d')
                
                # Verificar si la factura está dentro del rango de fechas          
                if fecha_inicio_dt <= fecha <= fecha_fin_dt:
                    fecha = factura.fecha.strftime('%Y-%m-%d')  # Formato de fecha
                    ventas_por_fecha[fecha] += float(alquiler.total)  # Sumar al total de la fecha
                
        # Ordenamos las fechas y preparamos los datos para la respuesta
        for fecha, total in ventas_por_fecha.items():
            ventas.append({
                "fecha": fecha,
                "total": total,
            })
            fechas.append(fecha)
            totales.append(total)
        
        ventas = sorted(ventas, key=lambda venta: venta["fecha"])  # Ordenamos por fecha
        fechas = [venta["fecha"] for venta in ventas]  # Fechas ordenadas
        totales = [venta["total"] for venta in ventas]  # Totales correspondientes
        context = {
            "ventas": ventas,
            'fechas': json.dumps(fechas), 
            "totales": json.dumps(totales), 
            "hotel": hotelInstancia,
            "administrador": personaInstancia,
            "ventasDias":ventasDias,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        }
        return render(request, "hotel/listado_ventas_hotel.html", context)
    else:
        
        
        fecha_inicio=  request.session['fecha_inicio_ventas-dias'] if "fecha_inicio_ventas-dias" in request.session else None
        fecha_fin=  request.session['fecha_fin_ventas-dias'] if "fecha_fin_ventas-dias" in request.session else None
        
        if fecha_inicio is None:
            context = {
                "hotel": hotelInstancia,
                "administrador": personaInstancia,
        }
            return render(request, "hotel/listado_ventas_hotel.html", context)
        
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        request.session['ventas_dias']= "ventas_dias"

        colHabitaciones = hotelInstancia.get_habitaciones()
        
        ventas = []
        fechas = []
        totales = []
        
        ventas_por_fecha = defaultdict(float)  # Diccionario para acumular las ventas por fecha
        
        for habitacion in colHabitaciones:
            alquileres = habitacion.alquileres.all()
            for alquiler in alquileres:
                factura = Factura.objects.get(id=alquiler.factura_id)
                fecha = factura.fecha.strftime('%Y-%m-%d')
                fecha = datetime.strptime(fecha, '%Y-%m-%d')
                
                # Verificar si la factura está dentro del rango de fechas          
                if fecha_inicio_dt <= fecha <= fecha_fin_dt:
                    fecha = factura.fecha.strftime('%Y-%m-%d')  # Formato de fecha
                    ventas_por_fecha[fecha] += float(alquiler.total)  # Sumar al total de la fecha
                
        # Ordenamos las fechas y preparamos los datos para la respuesta
        for fecha, total in ventas_por_fecha.items():
            ventas.append({
                "fecha": fecha,
                "total": total,
            })
            fechas.append(fecha)
            totales.append(total)
        
        ventas = sorted(ventas, key=lambda venta: venta["fecha"])  # Ordenamos por fecha
        fechas = [venta["fecha"] for venta in ventas]  # Fechas ordenadas
        totales = [venta["total"] for venta in ventas]  # Totales correspondientes

        
        context = {
            "ventas": ventas,
            'fechas': json.dumps(fechas), 
            "totales": json.dumps(totales), 
            "hotel": hotelInstancia,
            "administrador": personaInstancia,
            "ventasDias":ventasDias,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        }
        return render(request, "hotel/listado_ventas_hotel.html", context)


def ventasHotelPorMes(request, hotel):
    request.session['ventas_mes']= "ventas_mes"
    if 'ventas_dias' in request.session:
        del request.session['ventas_dias']
    ventasMes="ventas-mes"
    personaInstancia = request.user.persona
    hotelInstancia = get_object_or_404(Hotel, pk=hotel)
    colHabitaciones = hotelInstancia.get_habitaciones()
    print("colHabitaciones",colHabitaciones)
    
    ventas = []
    fechas = []
    totales = []
    
    ventas_por_mes = defaultdict(float)  # Diccionario para acumular las ventas por mes
    
    for habitacion in colHabitaciones:
        alquileres = habitacion.alquileres.all()
        for alquiler in alquileres:
            print("alquiler",alquiler)
            print("alquiler factura",alquiler.factura_id)
            factura = Factura.objects.get(id=alquiler.factura_id)
            print("factura",factura)
            # Extraemos el mes y año (formato 'YYYY-MM')
            mes = factura.fecha.strftime('%Y-%m')
            print("el meees", mes)
            
            ventas_por_mes[mes] += float(alquiler.total)  # Sumar al total del mes
            
    # Ordenamos los meses y preparamos los datos para la respuesta
    for mes, total in ventas_por_mes.items():
        ventas.append({
            "fecha": mes,
            "total": total,
        })
        fechas.append(mes)
        totales.append(total)
    
    ventas = sorted(ventas, key=lambda venta: venta["fecha"])  # Ordenar por fecha ascendente
    context = {
        "ventas": ventas,
        'fechas': json.dumps([venta["fecha"] for venta in ventas]),  # Fechas ordenadas
        "totales": json.dumps([venta["total"] for venta in ventas]),  # Totales correspondientes
        "hotel": hotelInstancia,
        "administrador": personaInstancia,
        "ventasMes": ventasMes,
    }
    return render(request, "hotel/listado_ventas_hotel.html", context)


def desafiliar_hotel(request, hotel):
    hotel = get_object_or_404(Hotel, pk=hotel)
    hotel.vendedores.clear()  # Vacía la relación de vendedores
    return redirect('hotel:hotel')