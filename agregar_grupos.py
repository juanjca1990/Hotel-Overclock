import os
import django


# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuenaVista.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group
from core.models import Persona

# Función para crear un grupo con permisos
def crear_grupo(nombre_grupo, permisos_codename):
    # Verificar si el grupo ya existe
    grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
    if creado:
        print(f"Grupo '{nombre_grupo}' creado.")
    else:
        print(f"Grupo '{nombre_grupo}' ya existe.")

    # Asignar permisos al grupo
    for codename in permisos_codename:
        try:
            permiso = Permission.objects.get(codename=codename)
            grupo.permissions.add(permiso)
            print(f"Permiso '{permiso.codename}' asignado al grupo '{nombre_grupo}'.")
        except Permission.DoesNotExist:
            print(f"Permiso '{codename}' no encontrado.")

    grupo.save()


def crear_usuario(username, email, password, first_name="", last_name="", grupo=None, superuser=False):
    
    usuario = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    if grupo:
        try:
            grupo_obj = Group.objects.get(name=grupo)
            usuario.groups.add(grupo_obj)
            print(f"Superusuario '{username}' asignado al grupo '{grupo}'.")
        except Group.DoesNotExist:
            print(f"El grupo '{grupo}' no existe.")
    usuario.save()
    
def crear_persona_para_usuario(username, tipo_documento, documento, nombre, apellido):
    try:
        # Busca el usuario por su nombre de usuario
        usuario = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"El usuario '{username}' no existe.")
        return
    
    persona = Persona(
        usuario=usuario,
        tipo_documento=tipo_documento,
        documento=documento,
        nombre=nombre,
        apellido=apellido,
    )
    persona.save()  # Guarda la instancia en la base de datos
    



if __name__ == '__main__':
    
    # Crea los grupos
    grupos_a_crear = {
        "Administrador" : ["add_logentry" , "change_logentry", "delete_logentry", "view_logentry", 
                           "add_user", "change_user", "delete_user", "view_user", 
                           "add_group", "change_group", "delete_group", "view_group", 
                           "add_permission", "change_permission", "delete_permission", "view_permission", 
                           "add_contenttype", "change_contenttype", "delete_contenttype", "view_contenttype", 
                           "add_pais", "change_pais", "delete_pais", "view_pais", 
                           "add_provincia", "change_provincia", "delete_provincia", "view_provincia",
                           "add_localidad", "change_localidad", "delete_localidad", "view_localidad",
                           "add_tipohabitacion", "change_tipohabitacion", "delete_tipohabitacion", "view_tipohabitacion",
                           "add_servicio", "change_servicio", "delete_servicio", "view_servicio",
                           "add_categoria", "change_categoria", "delete_categoria", "view_categoria",
                           "add_vendedor", "change_vendedor", "delete_vendedor", "view_vendedor",
                           "add_encargado", "change_encargado", "delete_encargado", "view_encargado",
                           "add_cliente", "change_cliente", "delete_cliente", "view_cliente", 
                           "add_factura", "change_factura", "delete_factura", "view_factura",
                           "add_persona", "change_persona", "delete_persona", "view_persona",
                           "add_rol", "change_rol", "delete_rol", "view_rol",
                           "add_descuento", "change_descuento", "delete_descuento", "view_descuento",
                           "add_habitacion", "change_habitacion", "delete_habitacion", "view_habitacion",
                           "add_hotel", "change_hotel", "delete_hotel", "view_hotel",
                           "add_paqueteturistico", "change_paqueteturistico", "delete_paqueteturistico", "view_paqueteturistico",
                           "add_precioportipo", "change_precioportipo", "delete_precioportipo", "view_precioportipo",
                           "add_temporadaalta", "change_temporadaalta", "delete_temporadaalta", "view_temporadaalta",
                           "add_session", "change_session", "delete_session", "view_session",
                           "add_alquiler", "change_alquiler", "delete_alquiler", "view_alquiler",
                           "add_liquidacion", "change_liquidacion", "delete_liquidacion", "view_liquidacion"],
        "Vendedor": ["add_tipo_pago", "change_tipo_pago", "delete_tipo_pago", "view_tipo_pago", "add_factura", "change_factura", "delete_factura", "view_factura"],

    }
    for nombre, permisos in grupos_a_crear.items():
        crear_grupo(nombre, permisos)
    
    # creo el superuser admin / admin para el primer acceso a la aplicacion ya con el grupo de administrador
    usuarios_a_crear = [
        {"username": "admin", "email": "supadmin@hotmail.com", "password": "admin", "first_name": "Super", "last_name": "Admin", "grupo": "Administrador", "superuser": True},]
    for usuario_data in usuarios_a_crear:
        crear_usuario(**usuario_data)

    # agrego a persona el administrador
    crear_persona_para_usuario(
        username='admin',  # Nombre de usuario del usuario existente
        tipo_documento='0',  # Tipo de documento (debe coincidir con las opciones)
        documento='12345678',  # Número de documento
        nombre='Super',        # Nombre de la persona
        apellido='Admin',       # Apellido de la persona
    )