from django.test import TestCase
from decimal import Decimal
from .models import (Pais, Provincia, Localidad, 
    Persona, Encargado, Vendedor, Cliente)

FIXTURES = [
    './core/fixtures/auth.json',
    './core/fixtures/base.json'
    ]

class ZonaTestCase(TestCase):
    fixtures = FIXTURES
    def setUp(self):
        # Parte 1: Mock, aislar lo que quiero probar
        self.trelew = Localidad.objects.filter(nombre="Trelew").first()
        self.rawson = Localidad.objects.create(nombre="Raswon", provincia=self.trelew.provincia)

    def test_crear_zona(self):

        # Parte 2: Ejecutar 
        zona_localidad = Localidad.objects.crear_zona("Trelew")
        zona_provincia = Localidad.objects.crear_zona("Chubut")
        zona_pais_arg = Localidad.objects.crear_zona("Argentina")
        zona_pais_br = Localidad.objects.crear_zona("Brasil")

        # Parte 3: Confirmacion 
        self.assertTrue(self.trelew in zona_localidad)
        self.assertTrue(self.trelew in zona_provincia)
        self.assertTrue(self.trelew in zona_pais_arg)
        self.assertTrue(self.rawson in zona_pais_arg)
        self.assertFalse(self.trelew in zona_pais_br)

class CategoriaTestCase(TestCase):
    fixtures = FIXTURES
    def setUp(self):
        pass

class PersonaTestCase(TestCase):
    fixtures = FIXTURES
    def setUp(self):
        self.persona = Persona.objects.create(
            nombre="Pepe", 
            tipo_documento=Persona.DNI,
            documento="23423435")

    def test_listar_vendedores(self):
        self.persona.hacer_vendedor("pepe", "pepe@gmail.com", "pepe")
        vendedores = Persona.objects.vendedores().filter(nombre="Pepe")
        self.assertEqual(len(vendedores), 1)

    def test_listar_encargados_con_dni(self):
        self.persona.hacer_vendedor("pepe", "pepe@gmail.com", "pepe")
        encargados = Persona.objects.encargados().filter(documento=23423435)
        self.assertEqual(len(encargados), 0)

class EncargadoTestCase(PersonaTestCase):
    def test_promover_encargado(self):
        self.persona.agregar_rol(Encargado())
        self.assertTrue(self.persona.sos(Encargado))
        self.assertTrue(len(self.persona.como(Encargado).clave) == 10)
        self.assertFalse(self.persona.como(Encargado).clave == "")

class VendedorTestCase(PersonaTestCase):
    def test_promover_vendedor(self):
        vendedor = self.persona.hacer_vendedor("pepe", "pepe@gmail.com", "pepe")
        vendedor.coeficiente = Decimal(5)
        vendedor.save()

        self.assertTrue(self.persona.sos(Vendedor))
        self.assertTrue(self.persona.como(Vendedor).coeficiente == Decimal(5))
        self.assertIsNotNone(self.persona.usuario)
        self.assertTrue(self.persona.usuario.has_perm('core.add_cliente'))
        self.assertFalse(self.persona.usuario.has_perm('core.add_servicio'))

#   Alta Vendedor
#   =============
#   Nombre:
#   Apellido:
#   Tipo:
#   Documento:
#   Ganancia:
#   -------------------
#   Email: 
#   Usuario:
#   Password:

#                  |Aceptar|

class ClienteTestCase(PersonaTestCase):
    def test_promover_cliente(self):
        self.persona.agregar_rol(Cliente())
        self.assertTrue(self.persona.sos(Cliente))
        self.assertTrue(self.persona.como(Cliente).puntos == 0)