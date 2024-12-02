from django.test import TestCase
from core.models import Cliente, Vendedor
from hotel.models import Hotel, PaqueteTuristico, Habitacion
from datetime import datetime
from .models import Factura, Liquidacion 
from .exceptions import MaxPasajerosException

FIXTURES = [
    './core/fixtures/auth.json',
    './core/fixtures/base.json',
    './hotel/fixtures/base.json',
    #'./venta/fixtures/base.json'
    ]

class FacturaTestCase(TestCase):
    fixtures = FIXTURES
    def setUp(self):
        self.hotel = Hotel.objects.first() 
        self.cliente = Cliente.objects.first() 
        self.vendedor = Vendedor.objects.first() 
        self.paquete = PaqueteTuristico.objects.first() 

    def test_alquilar_una_maximo_pasajeros(self):
        self.factura = Factura.objects.create(cliente=self.cliente, vendedor=self.vendedor)
        habitacion = self.hotel.habitaciones.first()
        habitaciones = [habitacion]
        # 5 noches en temporada alta = 1800, sin descuento
        with self.assertRaises(MaxPasajerosException):
            self.factura.alquilar_habitacion(habitacion, 
                2, 
                datetime(2021, 1, 1), 
                datetime(2021, 1, 6))

    def test_alquilar_una_habitacion(self):
        self.factura = Factura.objects.create(cliente=self.cliente, vendedor=self.vendedor)
        habitacion = self.hotel.habitaciones.first()
        # 5 noches en temporada alta = 1800, sin descuento
        alquiler = self.factura.alquilar_habitacion(habitacion, 
            1, 
            datetime(2021, 1, 1), 
            datetime(2021, 1, 6))
        self.assertEqual(alquiler.total, 5 * 1800)

    def test_alquilar_habitaciones(self):
        self.factura = Factura.objects.create(cliente=self.cliente, vendedor=self.vendedor)
        alquileres = list(self.factura.alquilar_habitaciones([
            (h, 1, datetime(2021, 1, 1), datetime(2021, 1, 6)) for h in self.hotel.habitaciones.all()]))
        #README: 2 habitaciones de 1800 cada una por 5 dias con descuento del 0.02%
        habitacion_1 = 5 * 1800
        habitacion_2 = 5 * 1800
        por_habitaciones = habitacion_1 + habitacion_2
        descuento = por_habitaciones * self.hotel.obtener_descuento_por_cantidad(2).coeficiente
        self.assertEqual(self.factura.total(), por_habitaciones - descuento)

    def test_alquilar_un_paquete(self):
        self.factura = Factura.objects.create(cliente=self.cliente, vendedor=self.vendedor)
        alquiler = self.factura.alquilar_paquete(self.paquete, [1])
        self.assertEqual(alquiler.total, (5 * 1800) - ((5 * 1800) * self.paquete.coeficiente))

    def test_liquidar_comision(self):
        self.factura = Factura.objects.create(cliente=self.cliente, vendedor=self.vendedor)
        habitacion = self.hotel.habitaciones.first()
        # 5 noches en temporada alta = 1800, sin descuento
        alquiler = self.factura.alquilar_habitacion(habitacion, 
            1, 
            datetime(2021, 1, 1), 
            datetime(2021, 1, 6))
        self.assertEqual(alquiler.total, 5 * 1800)
        liquidacion = Liquidacion.generar_para_vendedor(self.vendedor)
        self.assertEqual(liquidacion.total, 900)
