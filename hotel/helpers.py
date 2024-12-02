from hotel.models import Habitacion

def habitacion_duplicada(nueva_habitacion , hotel_id , form):
    habitaciones = Habitacion.objects.filter(hotel = hotel_id)
    for habitacion in habitaciones:
        if int(habitacion.numero) == int(nueva_habitacion) :
            form.add_error('numero', 'el numero de habitacion ya existe en este hotel')
            return True
            break
    return False


def hay_fechas_superpuestas(fecha_inicio, fecha_fin , fecha_inicio_paquete , fecha_fin_paquete):

    if((fecha_inicio <= fecha_inicio_paquete) and (fecha_fin >= fecha_fin_paquete)):
        return True
    else:
        if(fecha_inicio_paquete <= fecha_inicio <= fecha_fin_paquete):
            return True
        else:
            if(fecha_inicio_paquete <= fecha_fin <= fecha_fin_paquete):
                return True
    return False