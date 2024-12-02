
import re

def campo_valido_sin_numeros(campo , form , nombre_campo):
    pattern = r'^[a-zA-Z\s]+$'
    if not re.match(pattern, campo):
        form.add_error(nombre_campo, "el " + nombre_campo + " no puede contener numeros")
        return False
    return True