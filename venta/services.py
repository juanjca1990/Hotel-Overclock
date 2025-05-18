from datetime import datetime
from core.models import Persona, Vendedor
from hotel.models import Habitacion, PaqueteTuristico, PrecioPorTipo, TemporadaAlta
from venta.models import Alquiler, Factura, Liquidacion
from venta.helpers import cliente_existe

def buscar_monto_total_liquidaciones_pendientes(fecha_inicio, fecha_fin, vendedor):
    elementos = []
    if fecha_inicio is None or fecha_fin is None:
        facturas = Factura.objects.filter(
        liquidacion__isnull=True,
        vendedor=vendedor
    )
    else:
        facturas = Factura.objects.filter(
            liquidacion__isnull=True,
            vendedor=vendedor,
            fecha__range=(fecha_inicio, fecha_fin)
        )
    total = 0
    for factura in facturas:
        liquidaciones = Alquiler.objects.filter(factura_id=factura.pk)
        resultado_liquidado = (liquidaciones[0].total * 2) / 100
        total += resultado_liquidado
        fecha_liquidacion = factura.fecha
        factura_id = factura.pk
        elementos.append({'fecha': fecha_liquidacion, 'monto': total , 'factura_id': factura_id})
    return elementos

def cargar_liquidaciones_pendientes(fecha_inicio, fecha_fin, vendedor_id=None):
    if vendedor_id:
        vendedores = Vendedor.objects.filter(id=vendedor_id)
    else:
        vendedores = Vendedor.objects.all()
    facturas_pendientes = []
    for vendedor in vendedores:
        montos_pendientes = buscar_monto_total_liquidaciones_pendientes(fecha_inicio, fecha_fin, vendedor)
        for pendiente in montos_pendientes:
            persona_dict = {
                'nombre': vendedor.persona.nombre,
                'apellido': vendedor.persona.apellido,
                'documento': vendedor.persona.documento,
                'monto_total': pendiente['monto'],
                'fecha_liquidacion': pendiente['fecha'],
                'factura_id': pendiente['factura_id']
            }
            facturas_pendientes.append(persona_dict)
    return facturas_pendientes

def buscar_facturas_pendiente_de_liquidar(fecha_inicio, fecha_fin, vendedor):
    facturas = Factura.objects.filter(
        liquidacion__isnull=True,
        vendedor=vendedor,
        fecha__range=(fecha_inicio, fecha_fin)
    )
    return facturas

def liquidar_liquidaciones_pendientes(fecha_inicio, fecha_fin, documento):
    persona = Persona.objects.get(documento = documento)
    vendedor = Vendedor.objects.get(persona = persona)
    facturas_pendiente_de_liquidar = buscar_facturas_pendiente_de_liquidar(fecha_inicio, fecha_fin, vendedor)
    if len(facturas_pendiente_de_liquidar) > 0:
        monto_total = buscar_monto_total_liquidaciones_pendientes(fecha_inicio, fecha_fin, vendedor)
        liquidacion = Liquidacion(abonado=datetime.now(), vendedor=vendedor, total=monto_total)
        liquidacion.save()
        for factura_pendiente_de_liquidar in facturas_pendiente_de_liquidar:
            factura_pendiente_de_liquidar.liquidacion = liquidacion
            factura_pendiente_de_liquidar.save()
            

def documento_valido(dni_nuevo , form):
    if not dni_nuevo.isnumeric():
        form.add_error('documento', 'ingrese un documento valido')
        return False
    if cliente_existe(dni_nuevo):
        form.add_error('documento', 'DNI ya existe en el sistema')
        return False
    return True


def preparar_hoteles(hoteles, fecha_inicio, fecha_fin, num_pasajeros):
    arr = []
    for hotel in hoteles:
        disponible = hotel.disponible(fecha_inicio, fecha_fin, num_pasajeros)
        data={
            "id": hotel.pk,
            "nombre": hotel.nombre,
            "localidad" : hotel.localidad,
            "direccion" : hotel.direccion,
            "email" : hotel.email,
            "telefono" : hotel.telefono,
            "encargadoNombre": hotel.encargado.persona.nombre,
            "encargadoApellido" : hotel.encargado.persona.apellido,
            "categoria" : hotel.categoria,
            "dispuesto" : disponible
        }
        arr.append(data)
    return arr
        
def devolver_temporadas_en_fechas(temporadas, fecha_inicio, fecha_fin):
    temporadas_en_rango=[]
    for temporada in temporadas:
        if (( fecha_inicio <= temporada.inicio <= fecha_fin) or (fecha_inicio <= temporada.fin <= fecha_fin)):
            temporadas_en_rango.append(temporada)
    return temporadas_en_rango
    

def asignar_precio_por_temporada(fecha_inicio, fecha_fin, id_hotel, tipo_habitacion):
    temporadas = TemporadaAlta.objects.filter(hotel = id_hotel)
    precio_Hotel_temporadas = PrecioPorTipo.objects.filter( hotel_id = id_hotel, tipo_id = tipo_habitacion)
    dias_promocion = 0
    dias_sin_promocion = 0
    total = 0
    resultado = 0
    precio = precio_Hotel_temporadas.first()
    if (temporadas):
        temporadas = devolver_temporadas_en_fechas(temporadas, fecha_inicio, fecha_fin)
        if (temporadas):
            for temporada in temporadas:
                if (fecha_inicio <= fecha_fin <= temporada.inicio) or (temporada.fin <= fecha_inicio <= fecha_fin):
                    dias_sin_promocion = fecha_fin - fecha_inicio
                    dias_sin_promocion = dias_sin_promocion.days * precio.baja
                    total =  dias_sin_promocion
                
                if((fecha_inicio < temporada.inicio) and (temporada.inicio <= fecha_fin <= temporada.fin)):
                    dias_promocion = fecha_fin - temporada.inicio
                    dias_promocion = dias_promocion.days * precio.alta
                    dias_sin_promocion = temporada.inicio - fecha_inicio
                    dias_sin_promocion = dias_sin_promocion.days * precio.baja
                    total = dias_promocion + dias_sin_promocion
                
                if((temporada.inicio <= fecha_inicio <= temporada.fin) and (temporada.fin <= fecha_fin)):
                    dias_promocion = temporada.fin - fecha_inicio
                    dias_promocion = dias_promocion.days * precio.alta
                    dias_sin_promocion = fecha_fin - temporada.fin
                    dias_sin_promocion = dias_sin_promocion.days * precio.baja
                    total = dias_promocion + dias_sin_promocion
                
                if (temporada.inicio <= fecha_inicio) and (temporada.fin >= fecha_fin):
                    dias_promocion = fecha_fin - fecha_inicio
                    dias_promocion = dias_promocion.days * precio.alta
                    total = dias_promocion
                
                if ((fecha_inicio <= temporada.inicio <= temporada.fin) and (temporada.fin <= fecha_fin)):
                    dias_sin_promocion = (fecha_fin - temporada.fin ) + ( temporada.inicio - fecha_inicio)
                    dias_sin_promocion = dias_sin_promocion.days * precio.baja
                    dias_promocion = temporada.fin - temporada.inicio
                    dias_promocion = dias_promocion.days * precio.alta
                    total =  dias_promocion + dias_sin_promocion
                resultado = resultado + total
                fecha_inicio = temporada.fin
            return resultado
        else:
            if(fecha_inicio == fecha_fin):
                return precio.baja / 2
            else:
                return (fecha_fin - fecha_inicio).days * precio.baja
    else:  
        if(fecha_inicio == fecha_fin):
            return precio.baja / 2
        else:
            return (fecha_fin - fecha_inicio).days * precio.baja


def cargar_precio_habitacion_por_temporada(habitaciones, id_hotel, fecha_inicio, fecha_fin):
    habitaciones_con_precios=[]
    for habitacion in habitaciones:
        precio = asignar_precio_por_temporada(fecha_inicio, fecha_fin, id_hotel, habitacion.tipo_id )
        print("el precio" , precio)
        datos={
            "id": habitacion.id,
            "tipo": habitacion.tipo,
            "numero": habitacion.numero,
            "pasajeros": habitacion.tipo.pasajeros,
            "precio" : precio,
        }
        habitaciones_con_precios.append(datos)
    return habitaciones_con_precios


# elimino las habitaciones que se encuentran en paquetes promocionales de un hotel
def filtrar_habitaciones(habitaciones , paquetes) :  
    for paquete in paquetes:
        paq = PaqueteTuristico.objects.get(id = paquete.pk)
        lista=paq.habitaciones.all()
        for elemento in lista:
            for habitacion in habitaciones:
                if elemento.numero == habitacion.numero:
                    habitaciones.remove(habitacion)
    return habitaciones


