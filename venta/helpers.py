
from core.models import Persona


def cliente_existe(dni_nuevo_cliente):
    cliente = Persona.objects.filter(documento = dni_nuevo_cliente)
    if cliente:
        return True
    return False