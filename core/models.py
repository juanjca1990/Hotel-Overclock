from django.db import models
from django.contrib.auth.models import User, Group
from decimal import Decimal
from .utils import str_alfanumerico

# Pais, Provincia, Localidad
class Pais(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

    class Meta:
      verbose_name_plural = "Paises"


    def __str__(self):
        return self.nombre

class Provincia(models.Model):
    nombre = models.CharField(max_length=200 , unique=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class LocalidadManager(models.Manager):
    def crear_zona(self, nombre):
        query = models.Q(nombre__icontains=nombre) | \
            models.Q(provincia__nombre__icontains=nombre) | \
            models.Q(provincia__pais__nombre__icontains=nombre)
        return self.model.objects.filter(query)

class LocalidadQuerySet(models.QuerySet):
    pass

class Localidad(models.Model):
    objects = LocalidadManager.from_queryset(LocalidadQuerySet)()

    nombre = models.CharField(max_length=200)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
    class Meta:
        unique_together = (('nombre', 'provincia'), )

# Servicios, Categorias
class Servicio(models.Model):
    nombre = models.CharField(max_length=200 , unique=True)
    descripcion = models.CharField(max_length=800)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    ESTRELLA_A = 0
    ESTRELLA_B = 1
    ESTRELLA_C = 2
    ESTRELLA_1 = 3
    ESTRELLA_2 = 4
    ESTRELLA_3 = 5
    ESTRELLA_4 = 6
    ESTRELLA_5 = 7
    ESTRELLAS = (
        (ESTRELLA_A, "A"), 
        (ESTRELLA_B, "B"), 
        (ESTRELLA_C, "C"), 
        (ESTRELLA_1, "Tourist"), 
        (ESTRELLA_2, "Standard"), 
        (ESTRELLA_3, "Comfort"), 
        (ESTRELLA_4, "First Class"), 
        (ESTRELLA_5, "Luxury"), 
    )
   
    estrellas = models.PositiveSmallIntegerField(choices=ESTRELLAS)
    nombre = models.CharField(max_length=200 , unique= True)
    servicios = models.ManyToManyField(Servicio)

    def estrellasStr(self):
        return self.get_estrellas_display()
        
    def __str__(self):
        return self.nombre
    
    def get_servicios(self):
        return Servicio.objects.filter(categoria=self)
    
    

# Tipo De Habitacion
class TipoHabitacion(models.Model):
    nombre = models.CharField(max_length=200 , unique= True)
    descripcion = models.CharField(max_length=800)
    pasajeros = models.PositiveSmallIntegerField()
    # Cuartos para cuando el tipo es Departamento
    cuartos = models.PositiveSmallIntegerField(default = 0)

    def es_departamento(self):
        return self.cuartos == 0

    def __str__(self):
        return self.nombre

class PersonaManager(models.Manager):
    pass

class PersonaQuerySet(models.QuerySet):
    def vendedores(self):
        return self.filter(roles__tipo__exact=Vendedor.TIPO)

    def encargados(self):
        return self.filter(roles__tipo__exact=Encargado.TIPO)

    def clientes(self):
        return self.filter(roles__tipo__exact=Cliente.TIPO)

# Las Personas
class Persona(models.Model):
    DNI = 0
    PASAPORTE = 1
    LIBRETA = 2
    TIPOS_DOCUMENTO = (
        (DNI, "DNI"), 
        (PASAPORTE, "PASAPORTE"), 
        (LIBRETA, "LIBRETA")
    )
    objects = PersonaManager.from_queryset(PersonaQuerySet)()
    tipo_documento = models.PositiveSmallIntegerField(choices=TIPOS_DOCUMENTO)
    documento = models.CharField(max_length=13)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    imagen = models.ImageField(upload_to='media/perfiles/', blank=True, null=True)  # Agrega este campo

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    def como(self, Klass):
        return self.roles.get(tipo=Klass.TIPO).related()

    def agregar_rol(self, rol):
        if not self.sos(rol.__class__):
            rol.persona = self
            rol.save()

    def roles_related(self):
        return [rol.related() for rol in self.roles.all()]

    def sos(self, Klass):
        return any([isinstance(rol, Klass) for rol in self.roles_related()])
    
    def hacer_vendedor(self, user_name, email, password):
        vendedor = Vendedor()
        self.agregar_rol(vendedor)
        self.usuario = User.objects.create_user(user_name, email, password)
        self.usuario.groups.add(Group.objects.get(name="Vendedor"))
        self.save()
        return vendedor
        
    def hacer_encargado(self, clave):
        encargado = Encargado()
        self.agregar_rol(encargado)
        encargado.set_clave(clave)
        self.save()
        return encargado

    def hacer_cliente(self):
        cliente = Cliente()
        self.agregar_rol(cliente)
        self.save()
        return cliente


# Usamos patron roles para
# Encargados, Clientes, Vendedores
class Rol(models.Model):
    TIPO = 0
    TIPOS = [
        (0, "rol")
    ]
    persona = models.ForeignKey(Persona, related_name="roles", on_delete=models.CASCADE)
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.tipo = self.__class__.TIPO
        super(Rol, self).save(*args, **kwargs)

    def related(self):
        return self.__class__ != Rol and self or getattr(self, self.get_tipo_display())

    @classmethod
    def register(cls, klass):
        cls.TIPOS.append((klass.TIPO, klass.__name__.lower()))

    def __str__(self):
        return f"{self.get_tipo_display()} {self.persona}"

class Encargado(Rol):
    TIPO = 1
    bajaEncargado = models.BooleanField(default=False)
    # Clave Autogenerada? un token?
    # clave = models.CharField(max_length=10, default=lambda n = 10: str_alfanumerico(n))
    clave = models.CharField(max_length=10, default="")
    
    def set_clave(self, clave):
        self.clave = clave
        self.save()

    def set_baja(self):
        self.bajaEncargado = True
        self.save()

    def dar_alta(self):
        self.bajaEncargado = False 
        self.save()

class Vendedor(Rol):
    TIPO = 2
    estoyHabilitado = models.BooleanField(default=True) #Baja Logica 
    # Coeficiente de Ganancia
    coeficiente = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal(0))

    def set_baja(self):
        self.estoyHabilitado = False
        self.save()

    def dar_alta(self):
        self.estoyHabilitado = True 
        self.save()
        
class Cliente(Rol):
    TIPO = 3
    bajaCliente = models.BooleanField(default=False) #Baja Logica 
    
    puntos = models.PositiveIntegerField(default=0)

    def set_baja(self):
            self.bajaCliente = True
            self.save()

    def dar_alta(self):
        self.bajaCliente = False
        self.save()

    def agregar_puntos(self, factura):
        puntosFactura= int(factura.total()/5)
        self.puntos+=puntosFactura
        self.save()

    def quitar_puntos(self, factura):
        puntosFactura= int(factura.total())
        self.puntos-=puntosFactura
        self.save()

for Klass in [Encargado, Vendedor, Cliente]:
    Rol.register(Klass)