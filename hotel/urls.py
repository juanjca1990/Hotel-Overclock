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
app_name="hotel"



urlpatterns = [
    path('logout', cviews.logout),

    path('hotel',hviews.hotel, name="hotel"),
    path('crearHotel',hviews.hotelCrear, name="modalCrearHotel"),
    path('modificarHotel/<hotel>',hviews.hotelModificar, name="modalModificarHotel"),

    path('vistaHotel/<hotel>', hviews.detalleHotel, name="vistaHotel"),
    #Path GESTION TIPOHABITACION
    path('tipoHabitacionHotel/<hotel>', hviews.vistaTipoHabitacionHotel, name="tipoHabitacionHotel"),
    path('crearTipoHabitacion/<hotel>', hviews.tipoHabitacionCrear, name="modalCrearTipoHabitacion"), 
    path('modificarTipoHabitacion/<int:hotel>/<int:tipo>)', hviews.tipoHabitacionModificar, name="modalModificarTipoHabitacion"),
    path('eliminarTipoHabitacion/<int:hotel>/<int:tipo>)', hviews.tipoHabitacionEliminar, name="modalEliminarTipoHabitacion"),
    #Path GESTION HABITACION
    path('crearHabitacion/<hotel>', hviews.habitacionCrear, name="modalCrearHabitacion"), 
    path('eliminarHabitacion/<int:hotel>/<int:habitacion>)', hviews.habitacionEliminar, name="modalEliminarHabitacion"),
    path('reciclarHabitacion/<int:hotel>/<int:habitacion>)', hviews.habitacionReciclar, name="modalReciclarHabitacion"),
    #Path GESTION TEMPORADAS
    path('temporadaHotel/<hotel>', hviews.temporadaHotel, name="temporadaHotel"),
    path('crearTemporadaHotel/<hotel>',hviews.temporadaHotelCrear, name="modalCrearTemporadaHotel"),
    path('eliminarTemporada/<int:hotel>/<int:temporada>)', hviews.temporadaEliminar, name="modalEliminarTemporada"),
    path('modificarTemporada/<int:hotel>/<int:temporada>)', hviews.temporadaModificar, name="modalModificarTemporada"),
        
    #Path GESTION PAQUETES TURISTICOS
    path('paqueteTuristicoHotel/<hotel>', hviews.paqueteTuristicoHotel, name="paqueteTuristicoHotel"),
    path('crearPaqueteTuristicoHotel/<hotel>',hviews.paqueteTuristicoHotelCrear, name="modalCrearPaqueteTuristicoHotel"),
    path('modificarPaqueteTuristicoHotel/<int:hotel>/<int:paquete>',hviews.paqueteTuristicoHotelModificar, name="modalModificarPaqueteTuristicoHotel"),
    path('eliminarPaqueteTuristicoHotel/<int:hotel>/<int:paquete>',hviews.paqueteTuristicoHotelEliminar, name="modalEliminarPaqueteTuristicoHotel"),
    
    #Path GESTION SERVICIOS
    path('serviciosHotel/<hotel>', hviews.serviciosHotel, name="serviciosHotel"),
    path('aniadirserviciosHotel/<hotel>',hviews.aniadirServicioHotel, name="modalAniadirserviciosHotel"),
    path('eliminarserviciosHotel/<hotel>/<servicio>',hviews.eliminarServicioHotel, name="modalEliminarserviciosHotel"),
    
    #Path GESTION VENDEDORES HOTEL
    path('vendedoresHotel/<hotel>', hviews.vendedoresHotel, name="vendedoresHotel"),
    path('aniadirVendedorHotel/<hotel>',hviews.aniadirVendedorHotel, name="modalAniadirVendedorHotel"),
    path('eliminarVendedorHotel/<int:hotel>/<int:vendedor>',hviews.vendedorHotelEliminar, name="modalEliminarVendedorHotel"),
]
