import string
import random

def str_alfanumerico(n):
    clave = ""
    chars = string.ascii_letters + string.digits
    for _ in range(n):
        clave += chars[random.randint(0, len(chars) - 1)]
    return clave
