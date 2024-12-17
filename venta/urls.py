"""BuenaVista URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.admin.sites import all_sites
from django.urls import path, include
from hotel import views as hviews
from core import views as cviews
from venta import views as vviews
app_name="ventas"



urlpatterns = [
    path('logout', cviews.logout),

    path('vendedor',vviews.vendedor, name="vendedor"),
    path('iniciar_venta',vviews.iniciar_venta, name="iniciar_venta"),
    path('buscarHabitaciones/<hotel>', vviews.buscarHabitaciones, name="buscarHabitaciones"),
    path('vistaCliente/', vviews.vista_cliente, name="vistaCliente"),
    path('clienteAniadir/', vviews.cliente_aniadir, name="modalAniadirCliente"),
    path('clienteModificar/<cliente>', vviews.cliente_modificar, name="modalModificarCliente"),
    path('alquilarHabitacion/<habitacion>/<hotel>', vviews.alquilar_habitacion, name="alquilarHabitacion"),
    path('alquilarPaquete/<paquete>/<hotel>', vviews.alquilar_paquete, name="alquilarPaquete"),
    path('vistaCarrito/', vviews.vista_carrito, name="vistaCarrito"),
    path('quitarPaquete/<paquete>', vviews.quitar_paquete_carrito, name="quitarPaqueteCarrito"),
    path('quitarHabitacion/<habitacion>/<desde>/<hasta>', vviews.quitar_habitacion_carrito, name="quitarHabitacionCarrito"),
    path('seleccionarCliente/<cliente>' , vviews.seleccionar_cliente, name="seleccionarCliente"),
    path('facturarCarrito/' , vviews.facturar_carrito, name="facturarCarrito"),
    path('pagarFactura/<factura>' , vviews.pagar_factura, name="pagarFactura"),
    path('cancelarFactura/<factura>' , vviews.cancelarFactura, name="cancelarFactura"),
    path('limpiarPreferencias' , vviews.limpiar_preferencias, name="limpiar_preferencias"),
    path('listado_liquidaciones', vviews.listado_liquidaciones, name="listado_liquidaciones"),
    path('listaComprasCliente/<id_cliente>/<id_persona>', vviews.lista_compras_cliente, name="listaComprasCliente"),
    path('limpiarPreferenciasLiquidaciones' , vviews.limpiar_preferencias_liquidaciones, name="limpiar_preferencias_liquidaciones"),
    path('liquidar/<documento>/<id_factura>/<monto>', vviews.liquidar, name='liquidar'),
    path('limpiar_nombre_cliente' , vviews.limpiar_nombre_cliente, name="limpiar_nombre_cliente"),
    ]