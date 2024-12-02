from django.contrib import admin

from django.contrib import admin
from .models import (Hotel, Habitacion, PaqueteTuristico, TemporadaAlta, Descuento, PrecioPorTipo)

for model in [Hotel, Habitacion, PaqueteTuristico, TemporadaAlta, Descuento, PrecioPorTipo]:
    admin.site.register(model)
