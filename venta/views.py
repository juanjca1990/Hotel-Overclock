
from venta.models import Alquiler, Factura, Liquidacion, Tipo_pago
from venta.forms import ClienteForm
from django.shortcuts import render, redirect, get_object_or_404
from hotel.models import Habitacion, Hotel, PaqueteTuristico
from core.models import Persona, TipoHabitacion, Vendedor, Cliente
from hotel.models import Hotel
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from venta.carrito import Carrito
from venta.services import cargar_liquidaciones_pendientes, cargar_precio_habitacion_por_temporada, documento_valido, filtrar_habitaciones, liquidar_liquidaciones_pendientes, preparar_hoteles


# Create your views here.

@login_required
def vendedor(request):
    carrito = Carrito(request)
    if carrito.get_cliente()!=None: 
        print(carrito.get_cliente().persona.nombre)
    else:
        print("Aun no se ha seleccionado Cliente")
    contador=carrito.get_cantidad()
    personaInstancia = request.user.persona
    vendedorInstancia = get_object_or_404(Vendedor, persona = personaInstancia.id)
    colHoteles= Hotel.objects.filter(vendedores__persona=vendedorInstancia.persona)
    fecha_inicio=  request.session['fecha_inicio'] if "fecha_inicio" in request.session else None
    fecha_fin=  request.session['fecha_fin'] if "fecha_fin" in request.session else None
    pasajeros =  int(request.session['pasajeros']) if "pasajeros" in request.session else None
    hoteles_finales = []
    if fecha_inicio:
        formulario_enviado="enviado"
        hoteles_finales = preparar_hoteles(colHoteles,fecha_inicio,fecha_fin,pasajeros)
    else:
        formulario_enviado="no_enviado"
    return render(request, "venta/vendedor.html", {"colHoteles": hoteles_finales,"vendedor":vendedorInstancia,
        "pasajeros": pasajeros,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "formulario_enviado":formulario_enviado,
        "contador":contador
         })


        
def buscarHabitaciones(request,hotel):
    personaInstancia = request.user.persona
    vendedorInstancia = get_object_or_404(Vendedor, persona = personaInstancia.id)
    carrito = Carrito(request)
    contador=carrito.get_cantidad() 
    fecha_inicio=  datetime.strptime(request.session['fecha_inicio'], '%Y-%m-%d').date() if "fecha_inicio" in request.session else None
    fecha_fin=  datetime.strptime(request.session['fecha_fin'], '%Y-%m-%d').date() if "fecha_fin" in request.session else None
    pasajeros = int(request.session['pasajeros']) if "pasajeros" in request.session else None
    hotelInstancia = get_object_or_404(Hotel, pk=hotel)
    coleccionHabitaciones = hotelInstancia.get_habitaciones_busqueda(fecha_inicio,fecha_fin,pasajeros)
    colHabitaciones = [habitacion for habitacion in coleccionHabitaciones if habitacion.baja == False]
    ventas_habitaciones_en_carrito=carrito.get_alquileres_habitaciones()
    for venta in ventas_habitaciones_en_carrito:
        fecha_inicio_venta=datetime.strptime(venta.fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_venta=datetime.strptime(venta.fecha_fin, '%Y-%m-%d').date()
        for habitacion in colHabitaciones:
            pksiguales=str(habitacion.pk)==venta.habitacion
            inicio_alquiler_en_fechas_ingresadas=(fecha_inicio_venta>=fecha_inicio and fecha_inicio_venta<=fecha_fin)
            fin_alquiler_en_fechas_ingresadas=(fecha_fin_venta>=fecha_inicio and fecha_fin_venta<=fecha_fin)
            contenido_fechas=(fecha_inicio_venta<=fecha_inicio and fecha_fin_venta>=fecha_fin)
            if (pksiguales and (inicio_alquiler_en_fechas_ingresadas or fin_alquiler_en_fechas_ingresadas or contenido_fechas)):
                colHabitaciones.remove(habitacion)
    ventas_paquetes_en_carrito=carrito.get_alquileres_paquetes()
    colPaquetes = hotelInstancia.get_paquetes_busqueda(fecha_inicio,fecha_fin,pasajeros)
    for venta in ventas_paquetes_en_carrito:
        paquete=get_object_or_404(PaqueteTuristico,pk=venta.paquete)
        if paquete in colPaquetes:
            colPaquetes.remove(paquete)
            
    # elimino las habitaciones que estan en un paquete del carrito para que no se puedan alquilar
    for paquete in ventas_paquetes_en_carrito:
        #obtengo el paquete del hotel
        paquete_hotel = get_object_or_404(PaqueteTuristico, pk=paquete.paquete)
        # busco el paquete con sus habitaciones
        habitaciones_en_paquete = paquete_hotel.get_habitaciones()
        for habitacion in habitaciones_en_paquete:
            if habitacion in colHabitaciones:
                colHabitaciones.remove(habitacion)
    
    # elimino los paquetes donde una habitacion este en el carrito para q no se pueda alquilar
    for habitacion in ventas_habitaciones_en_carrito:
        habitacion_hotel = get_object_or_404(Habitacion, pk=habitacion.habitacion)
        for paquete in colPaquetes:
            habitaciones_en_paquete = paquete.get_habitaciones()
            # for habitacion_en_paquete in habitaciones_en_paquete:
            if habitacion_hotel in habitaciones_en_paquete:
                colPaquetes.remove(paquete)
    
    habitaciones_con_precio_final = cargar_precio_habitacion_por_temporada(colHabitaciones, hotelInstancia.pk, fecha_inicio, fecha_fin )
    return render(request, "venta/buscarHabitaciones.html", {"hotel":hotelInstancia,
        "habitaciones_disponibles": habitaciones_con_precio_final,
        "paquetes_disponibles":colPaquetes,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "vendedor":vendedorInstancia,
        "contador":contador
        })



def alquilar_habitacion(request, habitacion, hotel):
    carrito = Carrito(request)
    fecha_inicio=  datetime.strptime(request.session['fecha_inicio'], '%Y-%m-%d').date() if "fecha_inicio" in request.session else None
    fecha_fin=  datetime.strptime(request.session['fecha_fin'], '%Y-%m-%d').date() if "fecha_fin" in request.session else None
    pasajeros = int(request.session['pasajeros']) if "pasajeros" in request.session else None
    carrito.agregar_habitacion(habitacion, fecha_inicio, fecha_fin, pasajeros)
    return redirect("venta:buscarHabitaciones", hotel)


def alquilar_paquete(request, paquete, hotel):
    carrito = Carrito(request)
    pasajeros = int(request.session['pasajeros']) if "pasajeros" in request.session else None
    carrito.agregar_paquete(paquete, pasajeros)
    return redirect("venta:buscarHabitaciones",hotel)


def iniciar_venta(request):
    fechaInicio=request.POST['fecha_inicio']
    fechaFin=request.POST['fecha_fin']
    pasajeros=request.POST['pasajeros']
    request.session['fecha_inicio']=fechaInicio
    request.session['fecha_fin']=fechaFin
    request.session['pasajeros']=pasajeros
    return redirect('venta:vendedor')


def vista_cliente(request):
    colClientes=Cliente.objects.all()
    personaInstancia = request.user.persona
    vendedorInstancia = get_object_or_404(Vendedor, persona = personaInstancia.id)
    carrito = Carrito(request)
    contador=carrito.get_cantidad()
    return render(request, "venta/vista_cliente.html", {"colClientes": colClientes,"vendedor":vendedorInstancia,"contador":contador})


def cliente_aniadir(request):
    form = ClienteForm(request.POST)
    if request.method == "POST":
        dni_nuevo_cliente = request.POST['documento']
        if documento_valido(dni_nuevo_cliente , form):
            if form.is_valid():
                form.save()
                form.instance.hacer_cliente()              
                return redirect('venta:vistaCliente')
    return render(request,"venta/modals/modal_aniadir_cliente.html",{"formulario":form})    

def cliente_modificar(request,cliente):
    clienteInstancia=get_object_or_404(Cliente,pk=cliente)
    colClientes = Cliente.objects.all()
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=clienteInstancia)
        if form.is_valid():
            clienteInstancia.persona.nombre = request.POST['nombre']
            clienteInstancia.persona.apellido = request.POST['apellido']
            clienteInstancia.persona.documento = request.POST['documento']
            clienteInstancia.persona.tipo_documento = request.POST['tipo_documento']
            clienteInstancia.persona.save()
            clienteInstancia.save()
            return redirect('venta:vistaCliente')
        else:
            form = ClienteForm(request.POST, instance=clienteInstancia)
    else:
        form = ClienteForm(instance=clienteInstancia)
        form.fields["nombre"].initial = clienteInstancia.persona.nombre
        form.fields["apellido"].initial = clienteInstancia.persona.apellido
        form.fields["documento"].initial = clienteInstancia.persona.documento
        form.fields["tipo_documento"].initial = clienteInstancia.persona.tipo_documento
    return render(request,"venta/modals/modal_modificar_cliente.html",{"cliente":clienteInstancia,"formulario":form})

    
def vista_carrito(request):
    carrito=Carrito(request)
    coleccion_ventas = []
    total = 0
    if carrito.get_cantidad() > 0:
        coleccion_ventas = carrito.mostrar_carrito()
        total=float(str(coleccion_ventas['total']).strip("['|{|}]"))
    personaInstancia = request.user.persona
    vendedorInstancia = get_object_or_404(Vendedor, persona = personaInstancia.id)
    contador=carrito.get_cantidad()
    cliente=carrito.get_cliente()
    try:
        print(cliente.persona.nombre)
    except Exception:
        print("no hay persona seleccionada")
    print(carrito.get_vendedor().persona.nombre)
    return render(request,"venta/carrito.html",{"cliente":cliente,"vendedor":vendedorInstancia, "contador":contador, "coleccion_ventas":coleccion_ventas,"total":total})


def quitar_paquete_carrito(request, paquete):
    carrito=Carrito(request)
    carrito.quitar_paquete(paquete.strip("p"))
    return redirect('venta:vistaCarrito')

def quitar_habitacion_carrito(request, habitacion, desde, hasta):
    carrito=Carrito(request)
    habitacion=habitacion.split("-")
    fecha_desde=datetime.strptime(desde, '%Y-%m-%d').date()
    fecha_hasta=datetime.strptime(hasta, '%Y-%m-%d').date()
    carrito.quitar_habitacion(habitacion[1], fecha_desde, fecha_hasta)
    return redirect('venta:vistaCarrito')


def seleccionar_cliente(request, cliente):
    persona = Persona.objects.get(id = cliente)
    request.session['nombre_cliente']= persona.nombre
    request.session['apellido_cliente']=  persona.apellido
    request.session['dni_cliente']=  persona.documento
    carrito=Carrito(request)
    carrito.set_cliente(cliente)
    return redirect("venta:vendedor")

def facturar_carrito(request):
    carrito=Carrito(request)
    personaInstancia = request.user.persona
    vendedorInstancia = get_object_or_404(Vendedor, persona = personaInstancia.id)
    cliente=carrito.get_cliente()
    factura=Factura()
    factura.set_atributos(vendedorInstancia,cliente)
    factura.save()
    coleccion_alquileres_habitaciones=(carrito.get_alquileres_habitaciones())
    factura.alquilar_habitaciones(coleccion_alquileres_habitaciones)
    for paquete in carrito.get_paquetes_para_alquilar():
        factura.alquilar_paquete(paquete)

    coleccion_ventas = carrito.mostrar_carrito()
    total_carrito=float(str(coleccion_ventas['total']).strip("['|{|}]"))

    alcanzanPuntos= factura.cliente.puntos>= int(factura.total())+1
    return render(request,"venta/facturar_carrito.html",{"factura":factura, "alcanzanPuntos": alcanzanPuntos })

def pagar_factura(request, factura):
    print("APRETASTE EN PAGAAAAAAAAR")
    seleccionTipoPago=request.POST.get('opcionTipoPago')
    facturita= get_object_or_404(Factura, pk=factura)
    if seleccionTipoPago=="Puntos":   
        facturita.cliente.quitar_puntos(facturita)  
    else:
        if seleccionTipoPago=="Efectivo":
            facturita.cliente.agregar_puntos(facturita)
    tipoPago= get_object_or_404(Tipo_pago, nombre=seleccionTipoPago)
    facturita.tipo_pago=tipoPago
    facturita.save()
    carrito = Carrito(request)
    carrito.vaciar_carrito()
    return redirect("venta:vendedor")


def cancelarFactura(request,factura):
    print("CANCELANDO VENTAAAAAAAAAA!!!!!")
    facturita= get_object_or_404(Factura, pk=factura)
    for alquiler in facturita.get_alquileres():
        if alquiler.paquete is not None:
            alquiler.paquete.cancelar_venta()
    print("el id de la factura" , facturita.id)
    facturita.delete()
    carrito = Carrito(request)
    carrito.vaciar_carrito()
    return redirect("venta:vendedor")


def limpiar_preferencias(request):
    carrito = Carrito(request)
    carrito.set_cliente(None)
    if 'fecha_inicio' in request.session:
        del request.session['fecha_inicio']
    if 'fecha_fin' in request.session:
        del request.session['fecha_fin']
    if 'pasajeros' in request.session:
        del request.session['pasajeros']
    return redirect("venta:vendedor")


def limpiar_nombre_cliente(request):
    if 'nombre_cliente' in request.session:
        del request.session['nombre_cliente']
    if 'apellido_cliente' in request.session:
        del request.session['apellido_cliente']
    if 'dni_cliente' in request.session:
        del request.session['dni_cliente']
    return redirect("venta:vendedor")
    

def limpiar_preferencias_liquidaciones(request):
    if 'fecha_inicio_liquidaciones' in request.session:
        del request.session['fecha_inicio_liquidaciones']
    if 'fecha_fin_liquidaciones' in request.session:
        del request.session['fecha_fin_liquidaciones']
    return redirect("venta:listado_liquidaciones")

def listado_liquidaciones(request):
    personaInstancia = request.user.persona
    if request.method == "POST":
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        request.session['fecha_inicio_liquidaciones']=fecha_inicio
        request.session['fecha_fin_liquidaciones']=fecha_fin
        liquidaciones_pendientes = cargar_liquidaciones_pendientes(fecha_inicio, fecha_fin)
        context = {
            "liquidaciones_pendientes": liquidaciones_pendientes,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "administrador":personaInstancia,
        }
        return render(request, "venta/listado_liquidaciones.html",context)
    else:
        fecha_inicio=  request.session['fecha_inicio_liquidaciones'] if "fecha_inicio_liquidaciones" in request.session else None
        fecha_fin=  request.session['fecha_fin_liquidaciones'] if "fecha_fin_liquidaciones" in request.session else None
        liquidaciones_pendientes = cargar_liquidaciones_pendientes(fecha_inicio, fecha_fin)
        context = {
            "liquidaciones_pendientes": liquidaciones_pendientes,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "administrador":personaInstancia,
        }
        return render(request, "venta/listado_liquidaciones.html",context)


def liquidar(request,documento, id_factura,monto):
    vendedor = Vendedor.objects.get(persona__documento = documento)
    factura = Factura.objects.get(pk=id_factura)
    fecha_actual = datetime.now()
    
    # Crear una nueva instancia de Liquidacion
    liquidacion = Liquidacion.objects.create(
        fecha = factura.fecha,
        abonado= fecha_actual,
        vendedor_id=vendedor.id,
        total=monto
    )
    # Asigno la liquidacion a la factura
    factura.liquidacion_id = liquidacion.id
    factura.save()
    liquidacion.save()
    return redirect('venta:listado_liquidaciones')


def lista_compras_cliente(request, id_cliente , id_persona):
    cliente = Persona.objects.get(id = id_persona)
    print("id del cliente " , id_cliente)
    facturas = Factura.objects.filter(cliente_id = id_cliente)
    if facturas : # si existen facturas del cliente
        lista_compras=[]
        for factura in facturas :
            id_factura = factura.pk  
            pago = Tipo_pago.objects.get(id = factura.tipo_pago.pk)
            tipoPago = pago.nombre
            alquileres = Alquiler.objects.filter(factura_id = id_factura)  
            for alquiler in alquileres:
                contador_alquiler = 0
                fechainicio = alquiler.inicio
                fechafin = alquiler.fin
                total_gastado = alquiler.total
                habitaciones=[]   
                if alquiler.paquete :
                    # alquileres que se vendieron con paquetes
                    paqueteTuristico = PaqueteTuristico.objects.get( id = alquiler.paquete.pk)      
                    paqueteHabitacion = paqueteTuristico.get_habitaciones()
                    nombrePaquete = paqueteTuristico.nombre
                    habitacionesPaquetes = list(paqueteHabitacion)
                    hotel = Hotel.objects.get(id = alquiler.paquete.hotel_id)
                    nombre_hotel = hotel.nombre
                    nombreHabitacion=[]
                    for habitacionPaquete in habitacionesPaquetes:
                        habitacionPaquete = str(habitacionesPaquetes[contador_alquiler])
                        habitacionPaquete = habitacionPaquete.split(',')
                        habitacion_parte1 = habitacionPaquete[1]     
                        habitaciones.append(habitacion_parte1)
                        habitacion = habitacion_parte1.split(":")
                        numeroHabitacion = habitacion[1]      
                        contador_alquiler+=1       
                        habitacionHotel = Habitacion.objects.get(hotel_id = hotel.pk , numero = numeroHabitacion)       
                        nombreHabitacion.append(habitacionHotel.tipo)
                else:    
                    # habitaciones que se vendieron que no se encuentran en paquete
                    nombrePaquete="no se encuentra en paquete"
                    nombreHabitacion=[]
                    alquilersHabitaciones = alquiler.habitaciones.all()   
                    for alquilerHabitacion in alquilersHabitaciones:    
                        alquilerHabitacion  = str(alquilersHabitaciones[contador_alquiler])
                        alquilerHabitacion  = alquilerHabitacion.split(',')
                        habitacion_parte1 = alquilerHabitacion [1]  
                        nom_hotel= alquilerHabitacion[0]
                        nombre_hotel = nom_hotel.replace("Hotel ", "", 1) #saco el nombre de hotel
                        hotel = Hotel.objects.get(nombre = nombre_hotel)
                        habitaciones.append(habitacion_parte1)
                        habitacion = habitacion_parte1.split(":")
                        numeroHabitacion = habitacion[1]     
                        contador_alquiler+=1  
                        habitacionHotel = Habitacion.objects.get(hotel_id = hotel.pk , numero = numeroHabitacion)
                        nombreHabitacion.append(habitacionHotel.tipo)
                    
                nueva_compra ={ 'nombre_hotel': nombre_hotel,
                                'fecha_inicio': fechainicio,
                                'fecha_fin':fechafin,
                                'nombre_paquete': nombrePaquete,
                                'total_gastado': total_gastado,
                                'tipo_pago':tipoPago,
                                'paquete_habitacion': habitaciones,
                                'paquete_tipo_habitacion': nombreHabitacion}
            
                lista_compras.append(nueva_compra)
            
            context = {'cliente': cliente,
                    'lista_compras':lista_compras}
    else: #el cliente se inicio como tal pero no realizo todavia compras
        context = {'cliente': cliente}
        return render(request, 'venta/lista_compras_cliente.html' , context)
    
    return render(request, 'venta/lista_compras_cliente.html', context)


