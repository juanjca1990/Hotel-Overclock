
from django.db import models
from decimal import Decimal
from datetime import date, datetime, timedelta
from core.models import Localidad, Categoria, Servicio, TipoHabitacion, Vendedor, Encargado
from .exceptions import DescuentoException, TipoHotelException




class HotelManager(models.Manager):
    def en_zona(self, zona):
        return self.model.objects.filter(localidad__in=zona)

class HotelQuerySet(models.QuerySet):
    pass

# Hotel (Asignar Vendedor)
class Hotel(models.Model):
    objects = HotelManager.from_queryset(HotelQuerySet)()
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=800)
    #TODO: Email
    email = models.EmailField(max_length=200)
    telefono = models.CharField(max_length=200)
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE)
    encargado= models.ForeignKey(Encargado, on_delete=models.CASCADE, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(Servicio)
    tipos = models.ManyToManyField(TipoHabitacion, through='PrecioPorTipo', through_fields=('hotel', 'tipo'))
    vendedores = models.ManyToManyField(Vendedor)#, related_name="hoteles")
   
    def disponible(self, inicio, fin, pasajeros):
        habitaciones= self.habitaciones.filter(tipo__pasajeros__gte=pasajeros)
        return any([habitacion.disponible(inicio, fin) for habitacion in habitaciones]) 


    def get_tipos(self):
        return TipoHabitacion.objects.filter(hotel=self)

    def tengo_tipos(self):
        return self.tipos.count()>0

    def es_comercializable(self):
        return self.vendedores.count() > 0

    def es_hospedaje(self):
        return self.categoria.estrellas in [Categoria.ESTRELLA_A, Categoria.ESTRELLA_B, Categoria.ESTRELLA_C]

    def __str__(self):
        return f"Hospedaje {self.nombre}" if self.es_hospedaje() else f"Hotel {self.nombre}"

    def agregar_habitacion(self, tipo, numero):
        # TODO: Validar que el tipo seleccionado sea un tipo del hotel
        if not self.tipos.filter(pk=tipo.pk).exists():
            raise TipoHotelException(f"El hotel no trabaja con el tipo de habitación {tipo}")
        return Habitacion.objects.create(tipo=tipo, numero=numero, hotel=self)

    def agregar_tarifa(self, tipo, baja, alta):
        # Que pasa si ya tengo el tipo cargado en el hotel?
        # que pasa si baja es mas grande que alta?
        pass 

    def get_habitaciones(self):
        return Habitacion.objects.filter(hotel=self)

    def get_habitaciones_busqueda(self,fechai,fechaf,cantPasajeros):
        habitaciones= self.get_habitaciones()
        habitacionesBusqueda=[]
        for habitacion in habitaciones:
            if habitacion.disponible(fechai,fechaf) and (habitacion.tipo.pasajeros>=cantPasajeros):
                habitacionesBusqueda.append(habitacion)
        return habitacionesBusqueda

    def get_paquetes(self):
        return PaqueteTuristico.objects.filter(hotel=self)
    
    def get_paquetes_busqueda(self,fechai,fechaf,cantPasajeros):
        paquetesEnHotel = self.get_paquetes()
        print("paquetes en hoteldasdasdasd", paquetesEnHotel)
        paquetesSegunBusqueda=[]
        for paquete in paquetesEnHotel:
            print("dasdasdasdasda" , paquete.nombre)
            if (paquete.inicio <= fechai <=paquete.fin) and (paquete.fin<=fechaf) and (paquete.get_pasajeros()>=cantPasajeros) and (paquete.estoy_vigente()):
                paquetesSegunBusqueda.append(paquete)
            if ( paquete.inicio <= fechai <= fechaf) and (fechaf <= paquete.fin) and (paquete.get_pasajeros()>=cantPasajeros) and (paquete.estoy_vigente()):    
                paquetesSegunBusqueda.append(paquete)
            if (fechai <= paquete.inicio <= fechaf) and (fechaf <= paquete.fin) and (paquete.get_pasajeros()>=cantPasajeros) and (paquete.estoy_vigente()):    
                paquetesSegunBusqueda.append(paquete)
            if (fechai <= paquete.inicio <= fechaf) and (fechaf >= paquete.fin) and (paquete.get_pasajeros()>=cantPasajeros) and (paquete.estoy_vigente()):    
                paquetesSegunBusqueda.append(paquete)         
        return paquetesSegunBusqueda
    

    def get_temporadas(self):
        return TemporadaAlta.objects.filter(hotel=self)

    def agregar_descuento(self, habitaciones, coeficiente):
        if habitaciones <= 0:
            raise DescuentoException("El mínimo de habitaciones para aplicar descuento es de 1")
        if coeficiente < 0:
            raise DescuentoException("El descuento no puede ser negativo")
        # Condicion loca?
        if self.descuentos.filter(cantidad_habitaciones__lt=habitaciones, coeficiente__gt=coeficiente).exists():
            raise DescuentoException("No se puede crear un descuento menor a un descuento ya otorgado por menos habitaciones")
        return self.descuentos.create(cantidad_habitaciones=habitaciones, coeficiente=coeficiente)

    def obtener_descuento(self, habitaciones):
        return self.obtener_descuento_por_cantidad(len(habitaciones))

    def obtener_descuento_por_cantidad(self, cantidad):
        return self.descuentos.filter(cantidad_habitaciones__gte=cantidad).first()

    def get_servicios(self):
        return Servicio.objects.filter(hotel=self)

    def get_vendedores(self):
        return Vendedor.objects.filter(hotel=self)
        
    def get_categoria(self):
        return self.categoria

class PrecioPorTipo(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='tarifario')
    tipo = models.ForeignKey(TipoHabitacion, on_delete=models.CASCADE, related_name='hoteles')
    # Precio por noche
    baja = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    alta = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)

 
# Habitación
class Habitacion(models.Model):
    hotel = models.ForeignKey(Hotel, related_name="habitaciones", on_delete=models.CASCADE)
    numero = models.PositiveSmallIntegerField() # 403 <Piso><Cuarto>
    tipo = models.ForeignKey(TipoHabitacion, on_delete=models.CASCADE)
    baja = models.BooleanField(default=False) #Baja Logica 

    class Meta:
        unique_together = (('hotel', 'numero'), )

    def __str__(self):
        return f"{self.hotel}, Habitacion: {self.numero}"

    def precio_por_noche(self, fecha):
        precio_por_tipo = self.hotel.tarifario.filter(tipo=self.tipo).first()
        if precio_por_tipo is None:
            #TODO: Custom exception
            raise Exception("No puedo calcular el precio")
        if self.hotel.temporadas.filter(inicio__lte=fecha, fin__gte=fecha).exists():
            #print("es temp alta" + str(self.numero))
            return precio_por_tipo.alta
        #print("es temp baja" + str(self.numero))
        return precio_por_tipo.baja

    def precio_temp_baja(self):
        precio_por_tipo = self.hotel.tarifario.filter(tipo=self.tipo).first()
        if precio_por_tipo is None:
            #TODO: Custom exception
            raise Exception("No puedo calcular el precio")
        return precio_por_tipo.baja

    def precio_temp_alta(self):
        precio_por_tipo = self.hotel.tarifario.filter(tipo=self.tipo).first()
        if precio_por_tipo is None:
            #TODO: Custom exception
            raise Exception("No puedo calcular el precio")
        return precio_por_tipo.alta

    def precio_alquiler(self, desde, hasta):
        if desde >= hasta:
            #TODO: Custom exception
            raise Exception("No puedo calcular el precio ... precio_alquiler")
        total = Decimal(0)
        while desde < hasta:
            total += self.precio_por_noche(desde)
            desde += timedelta(days=1)
        return total


    def disponible(self ,desde, hasta):
        print(self.numero)
        alquileres = self.alquileres.all()
        desicion = False
        print(alquileres)
        for alquiler in alquileres:
            if ((str(alquiler.inicio) > str(hasta) ) and (self.baja == False)):
                desicion = True
            else:
                if ((str(alquiler.fin) < str(desde)) and (self.baja == False)):
                    desicion = True
                else:
                    desicion = False
        return desicion

    def get_pasajeros(self):
        return self.tipo.pasajeros

    def dar_baja(self):
        self.baja=True
 
    def dar_alta(self):
        self.baja=False
    

# Temporada Alta
class TemporadaAlta(models.Model):
    nombre = models.CharField(max_length=200)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="temporadas")
    inicio = models.DateField('fecha inicio')
    fin = models.DateField('fecha fin')

# Descuentos
class Descuento(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="descuentos")
    # 1 = coeficiente1 = 0 opcionalmente
    # 2 = coeficiente1
    # 3 = coeficiente2
    # 4 = coeficiente3
    # 5 = coeficiente4
    cantidad_habitaciones = models.PositiveSmallIntegerField()
    coeficiente = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        ordering = ["cantidad_habitaciones"]

# Paquete Turistico
class PaqueteTuristico(models.Model):
    nombre = models.CharField(max_length=200)
    coeficiente = models.DecimalField(max_digits=3, decimal_places=2)
    hotel = models.ForeignKey(Hotel, related_name='paquetesTuristicos', on_delete=models.CASCADE)
    inicio = models.DateField()
    fin = models.DateField()
    habitaciones = models.ManyToManyField(Habitacion, related_name='paqueteturistico')
    vendido = models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2)


    def actualizar_precio(self):
        self.precio=0
        #print(">>>>>>>>>>>>>>>>>>> calculando precio paquete: "+self.nombre+" >>>>>>>>>>>>>>>>>>>")
        habitaciones = Habitacion.objects.filter(paqueteturistico = self)
        for habitacion in habitaciones:
            #print("habitacion: " + str(habitacion.numero) +"precio: $"+ str(habitacion.precio_por_noche(self.inicio)) )
            self.precio += habitacion.precio_por_noche(self.inicio)

    def cantidad_dias(self):
        return abs(self.fin - self.inicio).days

    def get_costo(self):
        self.actualizar_precio()
        if(self.cantidad_dias() == 0):
            return "{0:.2f}".format(self.precio / 5)
        return "{0:.2f}".format((1-self.coeficiente) * (self.precio * self.cantidad_dias()))

    def tengo_habitacion(self,habitacion): 
        for item in self.habitaciones:
            if item.pk == habitacion.pk:
                return True
        return False

    def estoy_vigente(self):
        return (not self.vendido) and (self.fin >= date.today())
    
    def estoy_vencido(self):
        return (self.fin < date.today())
    
    def estoy_vendido(self):
        return (self.vendido)
            
    def marcar_venta(self):
        self.vendido=True
        self.save()
    
    def cancelar_venta(self):
        self.vendido=False
        self.save()

    def get_pasajeros(self):
        capacidad = 0
        habitaciones = Habitacion.objects.filter(paqueteturistico = self)
        for habitacion in habitaciones:
            capacidad+=habitacion.get_pasajeros()
        return capacidad

    def get_habitaciones(self):
        return self.habitaciones.all()
    
    def set_habitaciones(self , habitaciones):
        self.habitaciones = habitaciones
        self.save()
        
        