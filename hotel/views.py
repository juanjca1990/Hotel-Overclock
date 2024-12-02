from datetime import date, datetime
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
from .forms import  HabitacionForm, HotelForm, ServicioForm, TemporadaHotelForm, AgregarTipoAHotelForm, HabitacionForm, PaqueteTuristicoForm, VendedorHotelForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as do_login
from django.contrib.auth import logout
from django.contrib.auth.models import Group, User
from django.utils import timezone
from django.views.generic.edit import CreateView
from core.models import Persona, Vendedor, Categoria, TipoHabitacion, Servicio


# Create your views here.
@login_required
def hotel(request):
    personaInstancia = request.user.persona
    #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>",personaInstancia)
    colHoteles=Hotel.objects.all()
    return render(request, "hotel/hotelAdmin.html",{"colHoteles": colHoteles, "administrador":personaInstancia})

def hotelCrear(request):
    colHoteles = Hotel.objects.all()
    form = HotelForm(request.POST)
    
    if request.method == "POST":
            if form.is_valid():
                hotelInstancia=form.save()
                for servicio in hotelInstancia.categoria.servicios.all():
                    hotelInstancia.servicios.add(servicio)
                hotelInstancia.save()
                return redirect('hotel:hotel')
    return render(request, "hotel/modals/modal_hotel_crear.html", {"colHoteles": colHoteles, "formulario": form})

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
            print("dasdasdasdasdasdasdasdasdasdasdasd")
            print(formulario.errors)
            print("poirtpyoierptyoipretiypoeritp")
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


def tipoHabitacionEliminar(request,hotel,tipo): 
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    tipoHabitacionInstancia=get_object_or_404(PrecioPorTipo,pk=tipo)
    if request.method == 'POST':
        tipoHabitacionInstancia.delete()
        return redirect('hotel:tipoHabitacionHotel', hotel)
    return render(request, "hotel/modals/modal_tipoHabitacionHotel_eliminar.html",{"hotel":hotelInstancia ,"tipo":tipoHabitacionInstancia})
    



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
    hotelInstancia =get_object_or_404(Hotel, pk=hotel)
    habitacionInstancia=get_object_or_404(Habitacion,pk=habitacion)
    if request.method == "POST":
        habitacionInstancia.dar_baja()
        habitacionInstancia.save()
        return redirect('hotel:vistaHotel',hotel)
    return render(request, "hotel/modals/modal_habitacionHotel_eliminar.html",{"hotel":hotelInstancia,'habitacion':habitacionInstancia })

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
    hotel_actual=get_object_or_404(Hotel, pk=id_hotel)
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
            paquetes = habitacion.paqueteturistico.all() 
            for paquete in paquetes:
                if (hay_fechas_superpuestas(fecha_inicio ,fecha_fin , str(paquete.inicio), str(paquete.fin))):  
                    form.fields['habitaciones'].choices=[(c.pk,c.numero) for c in Habitacion.objects.filter(hotel=hotel_actual)]
                    form.add_error('habitaciones', 'alguna de las habitaciones seleccionadas ya tienen un paquete para ese periodo de fechas')
                    return render(request, "hotel/modals/modal_paqueteTuristicoHotel_crear.html", { "hotel": hotel_actual, "formulario": form})        
         
            # Crear un nuevo objeto PaqueteTuristico
            nuevo_paquete = PaqueteTuristico.objects.create(
                nombre=request.POST['nombre'],
                coeficiente = request.POST['coeficiente'],
                hotel = hotel_actual,
                inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
                fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date(),
                vendido=False,
                precio= 1
            )
            
            # Agregar las habitaciones seleccionadas al nuevo paquete
            for id_habitacion in id_habitaciones:
                habitacion = Habitacion.objects.get(id=id_habitacion)
                nuevo_paquete.habitaciones.add(habitacion)
            return redirect('hotel:paqueteTuristicoHotel', id_hotel)             
    form.fields['habitaciones'].choices=[(c.pk,c.numero) for c in Habitacion.objects.filter(hotel=hotel_actual)]
    return render(request, "hotel/modals/modal_paqueteTuristicoHotel_crear.html", { "hotel": hotel_actual, "formulario": form})


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
            print(paqueteInstancia)
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
        #print(hotelInstancia.vendedores)
        #form.save_m2m()
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

