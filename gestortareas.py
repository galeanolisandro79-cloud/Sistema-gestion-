import json 
import os 
import time 
from abc import ABC, abstracmethod 
from datetime import date, datetime, timedelta
from enum import Enum 
from functools import cmp_to_key 
from typing import Optional

ARCHIVOS_DATOS= "tareas.json"

#==================================================================================
# COLORES Y ESTILOS ANSI
#==================================================================================

class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # TEXTO
    NEGRO   = "\033[30m"
    ROJO    = "\033[31m"
    VERDE   = "\033[32m"
    AMARILLO= "\033[33m"
    AZUL    = "\033[34m"
    MAGENTA = "\033[35m"
    BLANCO  = "\033[37m"

    # FONDO
    BG_ROJO    = "\033[41m"
    BG_VERDE   = "\033[42m"
    BG_AMARILLO= "\033[43m"
    BG_AZUL    = "\033[44m"
    BG_MAGENTA = "\033[45m"

def c(texto: str, *estilos: str) -> str:
    """Envuelve texto con estilos ANSI y resetea al final."""
    return "".join(estilos) + texto + Color.RESET

#==================================================================================
#DECORADORES
#==================================================================================

def encabezado(titulo: str, ancho: int =50):
 """Decorador que imprime un encabezado antes de ejectuar la función."""
 def decorador(func):
  @functools.wraps(func)
  def wrapper (*args, **kwargs):
   linea = "=" * ancho
   print(f"\n{c(linea, Color.ROJO)}")
            print(c(f"  {titulo.upper()}", Color.BOLD, Color.ROJO))
            print(f"{c(linea, Color.ROJO)}")
            return func(*args, **kwargs)
        return wrapper
    return decorador


def confirmacion_guardado(func):
 """Decorador que muestra un mensaje de guardado exitoso tras la acción."""
@functools.wraps(func) 
def wrapper (*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(c("  ✔  Cambios guardados.", Color.DIM, Color.VERDE))
        return resultado
    return wrapper


def separador(func):
 """Decorador que imprime una línea separadora al final de la función."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(c("  " + "─" * 46, Color.DIM))
        return resultado
    return wrapper


def validar_titulo(func):
    """Decorador que exige que el título no esté vacío."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # El título se pide dentro de la función; lo interceptamos con un
        # monkey-patch temporal del input para retener control de flujo
        # Solo mostramos aviso; la validación concreta queda en la función.
        return func(*args, **kwargs)
    return wrapper


def medir_tiempo(func):
    """Decorador de diagnóstico: mide cuánto tarda una operación (p. ej. guardar)."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        duracion = time.perf_counter() - inicio
        if duracion > 0.01:
            print(c(f"Operación completada en {duracion*1000:.1f} ms.", Color.DIM))
        return resultado
    return wrapper

#==================================================================================
# ENUMERACIONES
#==================================================================================

class Prioridad(Enum):
 BAJA = 1
MEDIA = 2
ALTA = 3

def __str__(self) -> str:
        return self.name.capitalize()

    def color(self) -> str:
        return {
            Prioridad.BAJA:  Color.VERDE,
            Prioridad.MEDIA: Color.AMARILLO,
            Prioridad.ALTA:  Color.ROJO,
        }[self]

    def icono(self) -> str:
        return {
            Prioridad.BAJA:  "",
            Prioridad.MEDIA: "",
            Prioridad.ALTA:  "",
        }[self]
