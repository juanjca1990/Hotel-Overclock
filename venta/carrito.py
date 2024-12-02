from django.shortcuts import get_object_or_404
from hotel.models import Hotel, Habitacion, PaqueteTuristico
from core.models import Cliente, Vendedor
from datetime import datetime


class Carrito:
    vendedor=0
    cliente=None
    
    def __init__(self,request):
        self.request=request
        self.session=request.session
        carrito=self.session.get("carrito")
        #print(carrito)
        if carrito==None:
            print("SE CREA CARRITO!!!!!!!!")
            carrito=self.session["carrito"]={}
            self.carrito=carrito
        else:
            print("SE REUSA CARRITO!!!!!!!!")
            self.carrito=carrito
            
        self.cliente=self.session.get("cliente")
        self.vendedor=self.request.user.persona.id
        self.save()

    def save(self):
        self.session["carrito"]=self.carrito
        self.session.modified=True
    
    def get_cantidad(self):
        count=0
        for key,value in self.carrito.items():
            if "p" in key:
                count+=1
            else:
                count+=len(value["alquiler"])
        return count
    
    
    def limpiar_contador_items(self):
        self.carrito.clear()
                
    
    def vaciar_carrito(self):
        habitaciones = self.get_alquileres_habitaciones()
        paquetes = self.get_paquetes_para_alquilar()
        self.quitar_paquete(paquetes)
        for habitacion in habitaciones:
            self.quitar_habitacion(habitacion , habitacion.fecha_inicio , habitacion.fecha_fin)
        self.limpiar_contador_items()
        self.save()
           
#*************************GESTION HABITACION DE CARRITO **************************************
    def agregar_habitacion(self,habitacion,desde,hasta,pasajeros):
        claves=list(self.carrito.keys())
        if str(habitacion) not in claves:
            print("entre a crear un alquiler nuevo de otra habitacion")
            self.carrito[habitacion]={
                "alquiler":[]                
                }
            self.carrito[habitacion]["alquiler"].append([str(desde),str(hasta),str(pasajeros)])
            
        else:
            print("reuso la habitacion")
            periodoDisponible=True
            alquileres = list(self.carrito[str(habitacion)]["alquiler"])
            for index in alquileres:
                print(index)
                desde_contenido = (str(desde)>=index[0] and str(desde)<=index[1])
                hasta_contenido = (str(hasta)>=index[0] and str(hasta)<=index[1])
                esta_contenido = (str(desde)<=index[0] and str(hasta)>=index[1])
                print(desde_contenido," ",hasta_contenido," ",esta_contenido)
                if (desde_contenido or hasta_contenido or esta_contenido):
                    print("no puedo alquilar")
                    periodoDisponible=False
                    break
            if periodoDisponible:
                self.carrito[str(habitacion)]["alquiler"].append([str(desde),str(hasta),str(pasajeros)])
        self.save()

   
    
    def quitar_habitacion(self, habitacion, desde, hasta):
        claves=list(self.carrito.keys())
        if str(habitacion) in claves:
            if len(self.carrito[str(habitacion)]["alquiler"])==1:
                print("borro Habitacion")
                del self.carrito[str(habitacion)]
            else:
                print("busco alquiler")
                alquileres = list(self.carrito[str(habitacion)]["alquiler"])
                for index in alquileres:
                    if str(desde) and str(hasta) in index:
                        print("borro lo que encontre")
                        self.carrito[str(habitacion)]["alquiler"].remove(index)
        self.save()

#*************************GESTION PAQUETE DE CARRITO **************************************

    def agregar_paquete(self,paquete,pasajeros):
        paqueteInstancia=get_object_or_404(PaqueteTuristico,pk=paquete)
        clave_instancia="p"+str(paqueteInstancia.pk)
        claves=list(self.carrito.keys())
        if clave_instancia not in claves:
            print("entre a crear un alquiler nuevo de otro paquete")
            self.carrito[clave_instancia]={
                "fecha_inicio":str(paqueteInstancia.inicio),
                "fecha_fin":str(paqueteInstancia.fin),
                "nombre":paqueteInstancia.nombre,
                "paquete_pk":str(paqueteInstancia.pk),
                "pasajeros":str(pasajeros),    
                }
        else:
            print("imposible agregar")
        self.save()

    
    def quitar_paquete(self, paquete):
        if "p" in paquete:
            clave_instancia=paquete
        else:
            clave_instancia="p"+str(paquete)
        claves=list(self.carrito.keys())
        if clave_instancia in claves:
            del self.carrito[clave_instancia]
        else:
            print("no esta el paquete en el carrito")
        self.save()



    def get_alquileres_paquetes(self): 
        col_paquetes=[]
        for key,value in self.carrito.items():
            if "p" in str(key):
                paquete_pk=int(value["paquete_pk"])
                venta_paquete = Carrito_paquete(value['nombre'], value['fecha_inicio'], value['fecha_fin'], value['pasajeros'], paquete_pk)
                col_paquetes.append(venta_paquete)
        return col_paquetes


    def get_alquileres_habitaciones(self):
        col_habitaciones=[]
        for key,value in self.carrito.items():
            print(key)
            if "p" not in str(key):
                alquileres = value['alquiler']
                for alquiler in alquileres:
                    venta_habitacion = Carrito_habitacion(alquiler[0], alquiler[1], alquiler[2], key)
                    col_habitaciones.append(venta_habitacion)
        return col_habitaciones
    
#mostrar_carrito arma un diccionario para mostrar en el datatable en vistaCarrito, tanto paquetes como habitaciones

    def mostrar_carrito(self): 
        #hotel,descripcion,fechainicio,fechafin,costounitario,subtotal
        total=0
        col_paquetes=[]
        for key,value in self.carrito.items():
            if "p" in str(key):
                col_paquetes.append(get_object_or_404(PaqueteTuristico,pk=value["paquete_pk"]))
        lista_ventas={}
        if col_paquetes:
            for item in col_paquetes:
                lista_ventas["p"+str(item.pk)]={
                    "hotel":item.hotel.nombre,
                    "descripcion":"Paquete: "+ item.nombre,
                    "fecha_inicio":str(item.inicio),
                    "fecha_fin":str(item.fin),
                    "costo_unitario":str(item.get_costo()),
                    "subtotal":str(item.get_costo())}
                total+=float(item.get_costo())
        
        for key,value in self.carrito.items():
            if "p" not in str(key):
                habitacion=(get_object_or_404(Habitacion,pk=key))
                for alquiler in range(len(value["alquiler"])): # alquiler itera sobre la cantidad de veces alquilada la misma habitacion
                    clave=str(alquiler)+"-"+str(habitacion.pk)
                    lista_ventas[clave]={
                        "hotel":habitacion.hotel.nombre,
                        "descripcion":"Habitacion n°: "+ str(habitacion.numero),
                        "fecha_inicio":str(value["alquiler"][alquiler][0]),
                        "fecha_fin":str(value["alquiler"][alquiler][1]),
                        "costo_unitario":str(habitacion.precio_por_noche(datetime.strptime(str(value["alquiler"][alquiler][0]), '%Y-%m-%d').date())),
                        "subtotal":str(habitacion.precio_alquiler(datetime.strptime(str(value["alquiler"][alquiler][0]), '%Y-%m-%d').date(),datetime.strptime(value["alquiler"][alquiler][1], '%Y-%m-%d').date()))}
                    total+=float(habitacion.precio_alquiler(datetime.strptime(str(value["alquiler"][alquiler][0]), '%Y-%m-%d').date(),datetime.strptime(str(value["alquiler"][alquiler][1]), '%Y-%m-%d').date()))
        lista_ventas["total"]={str(total)}
        return lista_ventas


    def get_vendedor(self):
        vendedor= get_object_or_404(Vendedor, persona=self.vendedor)
        return vendedor

    def set_cliente(self, cliente):
        self.cliente=self.session["cliente"]=cliente
        self.save()

    def get_cliente(self):
        if self.cliente!= None:
            cliente= get_object_or_404(Cliente, persona =self.cliente)
            return cliente
        else:
            return None

#habitacion, huespedes, desde, hasta
    def get_paquetes_para_alquilar(self):
        coleccion_paquetes=self.get_alquileres_paquetes()
        coleccion_a_facturar=[]
        for paquete in coleccion_paquetes:
            coleccion_a_facturar.append(get_object_or_404(PaqueteTuristico,pk=paquete.paquete))
        return coleccion_a_facturar

class Carrito_venta:
    fecha_inicio = 0
    fecha_fin = 0
    pasajeros = 0
    def __init__(self, fecha_inicio, fecha_fin, pasajeros):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.pasajeros = pasajeros

class Carrito_habitacion(Carrito_venta):
    habitacion = None
    def __init__(self, fecha_inicio, fecha_fin, pasajeros, habitacion):
        Carrito_venta.__init__(self, fecha_inicio, fecha_fin, pasajeros)
        self.habitacion = habitacion
    

    def __str__(self):
        return("Numero: " + str(self.habitacion) + ", " + "Fecha inicio: "+ self.fecha_inicio + ", " + "Fecha fin: "+self.fecha_fin)


class Carrito_paquete(Carrito_venta):
    paquete = None
    nombre = ""
    def __init__(self, nombre, fecha_inicio, fecha_fin, pasajeros, paquete):
        Carrito_venta.__init__(self, fecha_inicio, fecha_fin, pasajeros)
        self.nombre = nombre
        self.paquete = paquete

    def __str__(self):
        return("Nombre: " + self.nombre + ", " + "Fecha inicio: "+ self.fecha_inicio + ", " + "Fecha fin: "+self.fecha_fin)

