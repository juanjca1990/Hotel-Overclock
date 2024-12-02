from django.test import TestCase
from decimal import Decimal
from core.models import Localidad, TipoHabitacion
from .models import Hotel, Habitacion 
from .exceptions import DescuentoException, TipoHotelException
from datetime import datetime

FIXTURES = [
    './core/fixtures/auth.json',
    './core/fixtures/base.json',
    './hotel/fixtures/base.json'
    ]

class HotelesTestCase(TestCase):
    fixtures = FIXTURES
    def setUp(self):
        self.hotel = Hotel.objects.first()
        self.tipo_habitacion = TipoHabitacion.objects.first()
        self.nuevo_tipo_habitacion = TipoHabitacion.objects.create(nombre="Nuevo Tipo", pasajeros=12)

    def test_buscar_en_zona(self):
        zona_trelew = Localidad.objects.crear_zona("Trelew")
        hoteles = Hotel.objects.en_zona(zona_trelew)
        self.assertEqual(len(hoteles), 1)
        hoteles = Hotel.objects.en_zona(Localidad.objects.crear_zona("Rawson"))
        self.assertEqual(len(hoteles), 0)

    def test_agregar_descuento_negativo(self):
        with self.assertRaises(DescuentoException):
            self.hotel.agregar_descuento(2, Decimal('-0.03'))
        
    def test_agregar_descuento_menor(self):
        with self.assertRaises(DescuentoException):
            self.hotel.agregar_descuento(2, Decimal('0.10'))
            self.hotel.agregar_descuento(3, Decimal('0.05'))

    def test_tarifa_por_tipo(self):
        self.hotel.agregar_tarifa(self.tipo_habitacion, 1300, 2000)

    def test_agregar_habitacion_sin_tipo(self):
        with self.assertRaises(TipoHotelException):
            self.hotel.agregar_habitacion(self.nuevo_tipo_habitacion, 202)

class HabitacionTestCase(TestCase):
    fixtures = FIXTURES
    def setUp(self):
        self.habitacion = Habitacion.objects.first()
        self.temporada_alta = datetime(2021, 1, 1)
        self.temporada_baja = datetime(2020, 11, 1)

    def test_precio_habitacion(self):
        self.assertTrue(self.habitacion.precio_por_noche(self.temporada_alta), 1800)
        self.assertTrue(self.habitacion.precio_por_noche(self.temporada_baja), 1500)