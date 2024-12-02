from django.contrib import admin

from django.contrib import admin
from .models import (Liquidacion, Factura, Alquiler, Tipo_pago)

for model in [Liquidacion, Factura, Alquiler, Tipo_pago]:
    admin.site.register(model)
