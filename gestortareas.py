"""
Sistema de gestión de tareas personales
TPI - Programación Orientada a Objetos

Conceptos aplicados:
  - Encapsulamiento: atributos privados expuestos solo via @property
  - Abstracción: Tarea y ComparadorTareas son clases abstractas (ABC)
  - Herencia: TareaSimple y TareaRecurrente heredan de Tarea
  - Polimorfismo: esta_vencida(), obtener_resumen() y comparar()
    se comportan distinto según la subclase que recibe el mensaje

Relaciones entre objetos:
  - Composición: GestorDeTareas contiene y es responsable de sus Tareas
  - Agregación: Tarea referencia a Categoria, que existe de forma independiente

Patrones de diseño:
  - Singleton: GestorDeTareas tiene una única instancia global
  - Strategy: ComparadorTareas permite cambiar el criterio de orden
    en tiempo de ejecución sin modificar GestorDeTareas

Para ejecutar: python3 gestortareas.py
"""

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from enum import Enum
from functools import cmp_to_key
from typing import Optional


# =============================================================================
# ENUMERACIONES
# =============================================================================

class Prioridad(Enum):
    BAJA = 1
    MEDIA = 2
    ALTA = 3

    def __str__(self) -> str:
        return self.name.capitalize()


class EstadoTarea(Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en progreso"
    COMPLETADA = "completada"

    def __str__(self) -> str:
        return self.value.capitalize()


# =============================================================================
# CATEGORIA
# Relación de agregación con Tarea: existe de forma independiente y puede
# ser compartida por varias tareas a la vez.
# =============================================================================

class Categoria:
    def __init__(self, nombre: str, color: str = "gris"):
        self._nombre = nombre
        self._color = color

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def color(self) -> str:
        return self._color

    def __str__(self) -> str:
        return self._nombre

    def __eq__(self, otra: object) -> bool:
        return isinstance(otra, Categoria) and self._nombre == otra._nombre

    def __hash__(self) -> int:
        return hash(self._nombre)


# =============================================================================
# TAREA (abstracta) + SUBCLASES
# Abstracción: Tarea declara el contrato sin implementarlo del todo.
# Herencia: TareaSimple y TareaRecurrente extienden Tarea.
# Polimorfismo: cada subclase redefine esta_vencida() y obtener_resumen().
# =============================================================================

class Tarea(ABC):
    _contador_id = 0

    def __init__(
        self,
        titulo: str,
        fecha_vencimiento: date,
        prioridad: Prioridad = Prioridad.MEDIA,
        categoria: Optional[Categoria] = None,
    ):
        Tarea._contador_id += 1
        self._id = Tarea._contador_id
        self._titulo = titulo
        self._fecha_creacion = date.today()
        self._fecha_vencimiento = fecha_vencimiento
        self._prioridad = prioridad
        self._estado = EstadoTarea.PENDIENTE
        self._categoria = categoria

    @property
    def id(self) -> int:
        return self._id

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def fecha_vencimiento(self) -> date:
        return self._fecha_vencimiento

    @property
    def prioridad(self) -> Prioridad:
        return self._prioridad

    @property
    def estado(self) -> EstadoTarea:
        return self._estado

    @property
    def categoria(self) -> Optional[Categoria]:
        return self._categoria

    def marcar_completada(self) -> None:
        self._estado = EstadoTarea.COMPLETADA

    def marcar_en_progreso(self) -> None:
        self._estado = EstadoTarea.EN_PROGRESO

    @abstractmethod
    def esta_vencida(self) -> bool:
        """Cada subclase define qué significa estar vencida para ella."""
        raise NotImplementedError

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Cada subclase arma su propia descripción para la consola."""
        raise NotImplementedError

    def _etiqueta_categoria(self) -> str:
        return f" [{self._categoria.nombre}]" if self._categoria else ""

    def __str__(self) -> str:
        return self.obtener_resumen()


class TareaSimple(Tarea):
    """Tarea de una sola vez con fecha límite fija."""

    def __init__(
        self,
        titulo: str,
        fecha_vencimiento: date,
        prioridad: Prioridad = Prioridad.MEDIA,
        categoria: Optional[Categoria] = None,
        notas: str = "",
    ):
        super().__init__(titulo, fecha_vencimiento, prioridad, categoria)
        self._notas = notas

    @property
    def notas(self) -> str:
        return self._notas

    def esta_vencida(self) -> bool:
        return (
            self._estado != EstadoTarea.COMPLETADA
            and date.today() > self._fecha_vencimiento
        )

    def obtener_resumen(self) -> str:
        marca = "VENCIDA" if self.esta_vencida() else str(self._estado)
        return (
            f"#{self._id} {self._titulo}{self._etiqueta_categoria()} "
            f"- vence {self._fecha_vencimiento} "
            f"- prioridad {self._prioridad} - {marca}"
        )


class TareaRecurrente(Tarea):
    """Tarea que se repite cada cierta cantidad de días.

    En vez de quedar vencida, al pasarse la fecha se reprograma
    automáticamente: ejemplo claro de polimorfismo, ya que
    esta_vencida() responde de forma completamente distinta a TareaSimple.
    """

    def __init__(
        self,
        titulo: str,
        fecha_vencimiento: date,
        frecuencia_dias: int,
        prioridad: Prioridad = Prioridad.MEDIA,
        categoria: Optional[Categoria] = None,
    ):
        super().__init__(titulo, fecha_vencimiento, prioridad, categoria)
        self._frecuencia_dias = frecuencia_dias

    @property
    def frecuencia_dias(self) -> int:
        return self._frecuencia_dias

    def esta_vencida(self) -> bool:
        if date.today() > self._fecha_vencimiento:
            self.reprogramar()
        return False

    def reprogramar(self) -> None:
        self._fecha_vencimiento += timedelta(days=self._frecuencia_dias)
        self._estado = EstadoTarea.PENDIENTE

    def obtener_resumen(self) -> str:
        return (
            f"#{self._id} {self._titulo}{self._etiqueta_categoria()} "
            f"(recurrente cada {self._frecuencia_dias} dias) "
            f"- proxima: {self._fecha_vencimiento} - {self._estado}"
        )


# =============================================================================
# PATRON STRATEGY: ComparadorTareas
# GestorDeTareas solo conoce la interfaz ComparadorTareas, nunca las
# clases concretas. Agregar un nuevo criterio de orden no requiere tocar
# el gestor (principio abierto/cerrado).
# =============================================================================

class ComparadorTareas(ABC):
    @abstractmethod
    def comparar(self, t1: Tarea, t2: Tarea) -> int:
        """Negativo si t1 va antes que t2, positivo si va después."""
        raise NotImplementedError

    def ordenar(self, tareas: list) -> list:
        return sorted(tareas, key=cmp_to_key(self.comparar))


class ComparadorPorPrioridad(ComparadorTareas):
    def comparar(self, t1: Tarea, t2: Tarea) -> int:
        return t2.prioridad.value - t1.prioridad.value  # alta primero


class ComparadorPorFechaVencimiento(ComparadorTareas):
    def comparar(self, t1: Tarea, t2: Tarea) -> int:
        if t1.fecha_vencimiento < t2.fecha_vencimiento:
            return -1
        if t1.fecha_vencimiento > t2.fecha_vencimiento:
            return 1
        return 0


# =============================================================================
# PATRON SINGLETON: GestorDeTareas
# Una única instancia centraliza todas las tareas y categorías del sistema.
# Relación de composición con Tarea: las tareas viven dentro del gestor.
# =============================================================================

class GestorDeTareas:
    _instancia: Optional["GestorDeTareas"] = None

    def __new__(cls) -> "GestorDeTareas":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        self._tareas: list[Tarea] = []
        self._categorias: dict[str, Categoria] = {}
        self._comparador: ComparadorTareas = ComparadorPorPrioridad()

    @classmethod
    def obtener_instancia(cls) -> "GestorDeTareas":
        return cls()

    def establecer_comparador(self, comparador: ComparadorTareas) -> None:
        self._comparador = comparador

    def agregar_tarea(self, tarea: Tarea) -> None:
        self._tareas.append(tarea)

    def eliminar_tarea(self, id_tarea: int) -> bool:
        tarea = self.buscar_tarea(id_tarea)
        if tarea is None:
            return False
        self._tareas.remove(tarea)
        return True

    def buscar_tarea(self, id_tarea: int) -> Optional[Tarea]:
        return next((t for t in self._tareas if t.id == id_tarea), None)

    def obtener_o_crear_categoria(self, nombre: str, color: str = "gris") -> Categoria:
        if nombre not in self._categorias:
            self._categorias[nombre] = Categoria(nombre, color)
        return self._categorias[nombre]

    def listar_tareas(self) -> list:
        return self._comparador.ordenar(self._tareas)

    def listar_pendientes(self) -> list:
        pendientes = [t for t in self._tareas if t.estado.name != "COMPLETADA"]
        return self._comparador.ordenar(pendientes)

    def listar_vencidas(self) -> list:
        return [t for t in self._tareas if t.esta_vencida()]


# =============================================================================
# INTERFAZ DE CONSOLA
# =============================================================================

def pedir_fecha(mensaje: str) -> date:
    while True:
        texto = input(mensaje).strip()
        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            print("Formato inválido. Usá AAAA-MM-DD, por ejemplo 2026-07-01.")


def pedir_prioridad() -> Prioridad:
    print("Prioridad: 1) Baja  2) Media  3) Alta")
    opcion = input("Elegí una opción [2]: ").strip() or "2"
    return {"1": Prioridad.BAJA, "2": Prioridad.MEDIA, "3": Prioridad.ALTA}.get(
        opcion, Prioridad.MEDIA
    )


def pedir_id(mensaje: str) -> int:
    while True:
        texto = input(mensaje).strip()
        if texto.isdigit():
            return int(texto)
        print("Ingresá un número de ID válido.")


def agregar_tarea_simple(gestor: GestorDeTareas) -> None:
    titulo = input("Título: ").strip()
    fecha = pedir_fecha("Fecha de vencimiento (AAAA-MM-DD): ")
    prioridad = pedir_prioridad()
    nombre_cat = input("Categoría (vacío = sin categoría): ").strip()
    categoria = gestor.obtener_o_crear_categoria(nombre_cat) if nombre_cat else None
    notas = input("Notas (opcional): ").strip()
    tarea = TareaSimple(titulo, fecha, prioridad, categoria, notas)
    gestor.agregar_tarea(tarea)
    print(f"Tarea creada -> {tarea}")


def agregar_tarea_recurrente(gestor: GestorDeTareas) -> None:
    titulo = input("Título: ").strip()
    fecha = pedir_fecha("Próxima fecha (AAAA-MM-DD): ")
    frecuencia = int(input("Frecuencia en días [7]: ").strip() or "7")
    prioridad = pedir_prioridad()
    nombre_cat = input("Categoría (vacío = sin categoría): ").strip()
    categoria = gestor.obtener_o_crear_categoria(nombre_cat) if nombre_cat else None
    tarea = TareaRecurrente(titulo, fecha, frecuencia, prioridad, categoria)
    gestor.agregar_tarea(tarea)
    print(f"Tarea creada -> {tarea}")


def listar(tareas: list) -> None:
    if not tareas:
        print("  (no hay tareas para mostrar)")
        return
    for tarea in tareas:
        print(f"  {tarea}")


def cambiar_criterio(gestor: GestorDeTareas) -> None:
    print("1) Por prioridad   2) Por fecha de vencimiento")
    opcion = input("Elegí una opción: ").strip()
    if opcion == "2":
        gestor.establecer_comparador(ComparadorPorFechaVencimiento())
        print("Orden actualizado: por fecha de vencimiento.")
    else:
        gestor.establecer_comparador(ComparadorPorPrioridad())
        print("Orden actualizado: por prioridad.")


def cargar_datos_ejemplo(gestor: GestorDeTareas) -> None:
    trabajo = gestor.obtener_o_crear_categoria("Trabajo", "azul")
    personal = gestor.obtener_o_crear_categoria("Personal", "verde")
    gestor.agregar_tarea(
        TareaSimple("Entregar informe mensual", date(2026, 6, 25), Prioridad.ALTA, trabajo)
    )
    gestor.agregar_tarea(
        TareaSimple("Comprar regalo de cumpleaños", date(2026, 6, 21), Prioridad.MEDIA, personal)
    )
    gestor.agregar_tarea(
        TareaRecurrente("Backup de la base de datos", date(2026, 6, 22), 7, Prioridad.ALTA, trabajo)
    )
    gestor.agregar_tarea(
        TareaSimple("Renovar el carnet", date(2026, 5, 1), Prioridad.BAJA, personal)
    )


def mostrar_menu() -> None:
    print(
        "\n--- Gestor de tareas personales ---\n"
        "1) Agregar tarea simple\n"
        "2) Agregar tarea recurrente\n"
        "3) Listar todas las tareas\n"
        "4) Listar tareas pendientes\n"
        "5) Listar tareas vencidas\n"
        "6) Marcar tarea como completada\n"
        "7) Eliminar tarea\n"
        "8) Cambiar criterio de orden\n"
        "9) Salir"
    )


def main() -> None:
    gestor = GestorDeTareas.obtener_instancia()
    cargar_datos_ejemplo(gestor)
    print("Se cargaron tareas de ejemplo para que puedas probar el sistema.")

    while True:
        mostrar_menu()
        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            agregar_tarea_simple(gestor)
        elif opcion == "2":
            agregar_tarea_recurrente(gestor)
        elif opcion == "3":
            listar(gestor.listar_tareas())
        elif opcion == "4":
            listar(gestor.listar_pendientes())
        elif opcion == "5":
            listar(gestor.listar_vencidas())
        elif opcion == "6":
            tarea = gestor.buscar_tarea(pedir_id("ID de la tarea: "))
            if tarea:
                tarea.marcar_completada()
                print("Tarea marcada como completada.")
            else:
                print("No se encontró esa tarea.")
        elif opcion == "7":
            if gestor.eliminar_tarea(pedir_id("ID de la tarea: ")):
                print("Tarea eliminada.")
            else:
                print("No se encontró esa tarea.")
        elif opcion == "8":
            cambiar_criterio(gestor)
        elif opcion == "9":
            print("¡Hasta la próxima!")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
