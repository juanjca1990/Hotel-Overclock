from datetime import datetime
from django.conf import settings
from django.db import models
from decimal import Decimal

from django.shortcuts import get_object_or_404
from core.models import Vendedor, Cliente
from hotel.models import Habitacion, PaqueteTuristico
from .exceptions import MaxPasajerosException

# a ponerse las pilas

# Liquidar Comision
class Liquidacion(models.Model):
    fecha = models.DateField(auto_now_add=True)
    abonado = models.DateField(null=True)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=20, decimal_places=2)

    def abonada(self):
        return self.abonado != None

    @staticmethod
    def generar_para_vendedor(vendedor):
        facturas = Factura.objects.filter(liquidacion__isnull=True, vendedor=vendedor)
        total = sum([f.total() for f in facturas]) * vendedor.coeficiente
        liquidacion = Liquidacion.objects.create(total=total, vendedor=vendedor)
        for f in facturas:
            f.liquidacion = liquidacion
            f.save()
        return liquidacion

class Tipo_pago(models.Model):
    nombre= models.CharField(max_length=200, unique=True)
     
    def pagar_factura(self, factura):
        #puntosNecesarios=int(factura.total()*0,2)
        #if factura.cliente.puntos>=puntosNecesarios:
        self.monto=factura.total()
        factura.tipo_pago=self
        #factura.cliente.quitar_puntos(factura)
        factura.save()
        #factura.cliente.agregar_puntos(factura)


class Factura(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    liquidacion = models.ForeignKey(Liquidacion, null=True, blank=True, on_delete=models.SET_NULL)
    tipo_pago=models.ForeignKey(Tipo_pago, null=True, blank=True, on_delete=models.SET_NULL)
    fecha = models.DateField(auto_now_add=True)

    def set_atributos(self,vendedor,cliente):
        self.cliente=cliente
        self.vendedor=vendedor

    def alquilar_habitaciones(self, habitaciones_con_fecha):
        alquileres = []
        for alquiler_habitacion in habitaciones_con_fecha:
            habitacion=get_object_or_404(Habitacion, pk=alquiler_habitacion.habitacion)
            fecha_inicio_venta=datetime.strptime(alquiler_habitacion.fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_venta=datetime.strptime(alquiler_habitacion.fecha_fin, '%Y-%m-%d').date()
            alquiler = self.alquilar_habitacion(habitacion, int(alquiler_habitacion.pasajeros), fecha_inicio_venta,fecha_fin_venta)
            if alquiler not in alquileres:
                alquileres.append(alquiler)
        return alquileres 

    def alquilar_habitacion(self, habitacion, huespedes, desde, hasta, paquete = None):
        if huespedes > habitacion.tipo.pasajeros + settings.TOLERANCIA_PASAJEROS:
            #TODO: Custom exception
            raise MaxPasajerosException(f"No puede superar la cantidad de pasajeros permitida: {habitacion.tipo.pasajeros}")
        hotel = habitacion.hotel
        alquiler = self.alquileres.filter(habitaciones__hotel__in=[hotel], inicio=desde, fin=hasta).first()
        if alquiler is None:
            alquiler = Alquiler.objects.create(cantidad_huespedes=huespedes, inicio=desde, fin=hasta, factura=self, paquete=paquete)
        alquiler.habitaciones.add(habitacion)
        descuento = hotel.obtener_descuento(alquiler.habitaciones.all())
        alquiler.total = sum([h.precio_alquiler(desde, hasta) for h in alquiler.habitaciones.all()])
        if descuento is not None:
            alquiler.total -= alquiler.total * descuento.coeficiente
        alquiler.save()
        return alquiler

    def alquilar_paquete(self, paquete):
        for habitacion in (paquete.habitaciones.all()):
            alquiler = self.alquilar_habitacion(habitacion, habitacion.tipo.pasajeros, paquete.inicio, paquete.fin, paquete=paquete) 
        alquiler.total -= alquiler.total * paquete.coeficiente
        alquiler.paquete=paquete
        alquiler.save()
        paquete.marcar_venta()
        paquete.save()
        return alquiler
    
    def total(self):
        return sum([a.total for a in self.alquileres.all()])

    def get_alquileres(self):
        return Alquiler.objects.filter(factura=self)
        

# Alquiler
class Alquiler(models.Model):
    factura = models.ForeignKey(Factura, related_name="alquileres", on_delete=models.CASCADE)
    # De un mismo hotel
    habitaciones = models.ManyToManyField(Habitacion, related_name="alquileres")
    paquete = models.OneToOneField(PaqueteTuristico, null=True, blank=True, on_delete=models.SET_NULL, related_name="alquiler")
    cantidad_huespedes = models.PositiveSmallIntegerField()
    inicio = models.DateField()
    fin = models.DateField()
    total = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal(0))
    #PaqueteTuristico.objects.filter(alquiler__isnull=True) para obtener paquetes no vendidos!

    def get_hotel(self):
        print("HOTEL DE M:", self.habitaciones.all().first().hotel)
        return self.habitaciones.all().first().hotel

    def get_habitaciones(self):
        return self.habitaciones.all()

    def get_cantidad_habitaciones(self):
        return self.habitaciones.all().count()  
    
    def habitacion_disponible_entre_fechas(fecha_alquiler_inicio, fecha_alquiler_fin):
        if(fecha_alquiler_inicio <= self.inicio <= fecha_alquiler_fin) and (fecha_alquiler_inicio <= self.fin <= fecha_alquiler_fin):
            return False
        else:
            return True 




        
        



