from django.contrib import admin
from .models import (
  Pais, Localidad, Provincia, Categoria, Servicio,
  TipoHabitacion, Persona, Cliente, Encargado, Vendedor)

for model in [Pais, Provincia, Persona, Localidad, Categoria, Servicio, TipoHabitacion, Cliente, Encargado, Vendedor]:
    admin.site.register(model)
