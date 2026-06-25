import json
import os
import re
import functools
import time
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from enum import Enum
from functools import cmp_to_key
from typing import Optional

ARCHIVO_DATOS = "tareas.json"


# =============================================================================
# COLORES Y ESTILOS ANSI
# =============================================================================

class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    NEGRO   = "\033[30m"
    ROJO    = "\033[31m"
    VERDE   = "\033[32m"
    AMARILLO= "\033[33m"
    AZUL    = "\033[34m"
    MAGENTA = "\033[35m"
    BLANCO  = "\033[37m"

    BG_ROJO    = "\033[41m"
    BG_VERDE   = "\033[42m"
    BG_AMARILLO= "\033[43m"
    BG_AZUL    = "\033[44m"
    BG_MAGENTA = "\033[45m"


def c(texto: str, *estilos: str) -> str:
    return "".join(estilos) + texto + Color.RESET


_ANSI_RE = re.compile(r'\033\[[0-9;]*m')

def len_visible(texto: str) -> int:
    """Devuelve el largo visual del texto ignorando los códigos ANSI."""
    return len(_ANSI_RE.sub('', texto))


# =============================================================================
# DECORADORES DE CONSOLA
# =============================================================================

def encabezado(titulo: str, ancho: int = 50):
    def decorador(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            linea = "═" * ancho
            print(f"\n{c(linea, Color.ROJO)}")
            print(c(f"  {titulo.upper()}", Color.BOLD, Color.ROJO))
            print(f"{c(linea, Color.ROJO)}")
            return func(*args, **kwargs)
        return wrapper
    return decorador


def confirmacion_guardado(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(c("Cambios guardados.", Color.DIM, Color.VERDE))
        return resultado
    return wrapper


def separador(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(c("  " + "─" * 46, Color.DIM))
        return resultado
    return wrapper


def validar_titulo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def medir_tiempo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        duracion = time.perf_counter() - inicio
        if duracion > 0.01:
            print(c(f"Operación completada en {duracion*1000:.1f} ms.", Color.DIM))
        return resultado
    return wrapper


# =============================================================================
# ENUMERACIONES
# =============================================================================

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


class EstadoTarea(Enum):
    PENDIENTE   = "Pendiente"
    EN_PROGRESO = "En progreso"
    COMPLETADA  = "Completada"

    def __str__(self) -> str:
        return self.value.capitalize()

    def color(self) -> str:
        return {
            EstadoTarea.PENDIENTE:   Color.AMARILLO,
            EstadoTarea.EN_PROGRESO: Color.ROJO,
            EstadoTarea.COMPLETADA:  Color.VERDE,
        }[self]

    def icono(self) -> str:
        return {
            EstadoTarea.PENDIENTE:   "",
            EstadoTarea.EN_PROGRESO: "",
            EstadoTarea.COMPLETADA:  "",
        }[self]


# =============================================================================
# CATEGORIA
# =============================================================================

class Categoria:
    _ANSI = {
        "azul":    Color.AZUL,
        "verde":   Color.VERDE,
        "rojo":    Color.ROJO,
        "amarillo":Color.AMARILLO,
        "magenta": Color.MAGENTA,
        "gris":    Color.DIM,
    }

    def __init__(self, nombre: str, color: str = "gris"):
        self._nombre = nombre
        self._color  = color

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def color(self) -> str:
        return self._color

    def __str__(self) -> str:
        ansi = self._ANSI.get(self._color, Color.DIM)
        return c(f"[{self._nombre}]", ansi, Color.BOLD)

    def __eq__(self, otra: object) -> bool:
        return isinstance(otra, Categoria) and self._nombre == otra._nombre

    def __hash__(self) -> int:
        return hash(self._nombre)


# =============================================================================
# TAREA (abstracta) + SUBCLASES
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
        self._id               = Tarea._contador_id
        self._titulo           = titulo
        self._fecha_creacion   = date.today()
        self._fecha_vencimiento= fecha_vencimiento
        self._prioridad        = prioridad
        self._estado           = EstadoTarea.PENDIENTE
        self._categoria        = categoria

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
        raise NotImplementedError

    @abstractmethod
    def obtener_resumen(self) -> str:
        raise NotImplementedError

    def _etiqueta_categoria(self) -> str:
        return f" {self._categoria}" if self._categoria else ""

    def __str__(self) -> str:
        return self.obtener_resumen()


class TareaSimple(Tarea):

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
        id_str     = c(f"#{self._id:<3}", Color.DIM)
        titulo_str = c(self._titulo, Color.BOLD)
        cat_str    = self._etiqueta_categoria()
        fecha_str  = c(str(self._fecha_vencimiento), Color.ROJO)
        prio_icon  = self._prioridad.icono()
        prio_str   = c(f"{prio_icon} {self._prioridad}", self._prioridad.color())

        if self.esta_vencida():
            estado_str = c("VENCIDA", Color.BOLD, Color.BG_MAGENTA, Color.BLANCO)
        else:
            ico = self._estado.icono()
            estado_str = c(f"{ico} {self._estado}", self._estado.color())

        return f"  {id_str} {titulo_str}{cat_str}  vence {fecha_str}  {prio_str}  {estado_str}"


class TareaRecurrente(Tarea):

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
        id_str     = c(f"{self._id:<3}", Color.DIM)
        titulo_str = c(self._titulo, Color.BOLD)
        cat_str    = self._etiqueta_categoria()
        frec_str   = c(f"cada {self._frecuencia_dias}d", Color.MAGENTA)
        fecha_str  = c(str(self._fecha_vencimiento), Color.ROJO)
        prio_icon  = self._prioridad.icono()
        prio_str   = c(f"{prio_icon} {self._prioridad}", self._prioridad.color())
        ico        = self._estado.icono()
        estado_str = c(f"{ico} {self._estado}", self._estado.color())

        return (
            f"  {id_str} {titulo_str}{cat_str}  {frec_str}  próxima {fecha_str}  "
            f"{prio_str}  {estado_str}"
        )


# =============================================================================
# PATRON STRATEGY: ComparadorTareas
# =============================================================================

class ComparadorTareas(ABC):
    @abstractmethod
    def comparar(self, t1: Tarea, t2: Tarea) -> int:
        raise NotImplementedError

    def ordenar(self, tareas: list) -> list:
        return sorted(tareas, key=cmp_to_key(self.comparar))


class ComparadorPorPrioridad(ComparadorTareas):
    def comparar(self, t1: Tarea, t2: Tarea) -> int:
        return t2.prioridad.value - t1.prioridad.value


class ComparadorPorFechaVencimiento(ComparadorTareas):
    def comparar(self, t1: Tarea, t2: Tarea) -> int:
        if t1.fecha_vencimiento < t2.fecha_vencimiento:
            return -1
        if t1.fecha_vencimiento > t2.fecha_vencimiento:
            return 1
        return 0


# =============================================================================
# SERIALIZACION
# =============================================================================

def _tarea_a_dict(tarea: "Tarea") -> dict:
    base = {
        "id":               tarea.id,
        "titulo":           tarea.titulo,
        "fecha_vencimiento":tarea.fecha_vencimiento.isoformat(),
        "prioridad":        tarea.prioridad.name,
        "estado":           tarea.estado.name,
        "categoria":        tarea.categoria.nombre if tarea.categoria else None,
        "categoria_color":  tarea.categoria.color  if tarea.categoria else None,
    }
    if isinstance(tarea, TareaRecurrente):
        base["tipo"] = "recurrente"
        base["frecuencia_dias"] = tarea.frecuencia_dias
    else:
        base["tipo"]  = "simple"
        base["notas"] = tarea.notas
    return base


def _tarea_desde_dict(datos: dict, gestor: "GestorDeTareas") -> "Tarea":
    categoria = None
    if datos.get("categoria"):
        categoria = gestor.obtener_o_crear_categoria(
            datos["categoria"], datos.get("categoria_color", "gris")
        )
    fecha     = date.fromisoformat(datos["fecha_vencimiento"])
    prioridad = Prioridad[datos["prioridad"]]

    if datos["tipo"] == "recurrente":
        tarea = TareaRecurrente(
            datos["titulo"], fecha, datos["frecuencia_dias"], prioridad, categoria
        )
    else:
        tarea = TareaSimple(
            datos["titulo"], fecha, prioridad, categoria, datos.get("notas", "")
        )

    tarea._id     = datos["id"]
    tarea._estado = EstadoTarea[datos["estado"]]
    Tarea._contador_id = max(Tarea._contador_id, datos["id"])
    return tarea


# =============================================================================
# PATRON SINGLETON: GestorDeTareas
# =============================================================================

class GestorDeTareas:
    _instancia: Optional["GestorDeTareas"] = None

    def __new__(cls) -> "GestorDeTareas":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        self._tareas:      list[Tarea]          = []
        self._categorias:  dict[str, Categoria] = {}
        self._comparador:  ComparadorTareas     = ComparadorPorPrioridad()

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
        pendientes = [
            t for t in self._tareas
            if t.estado.name != "COMPLETADA" and not t.esta_vencida()
        ]
        return self._comparador.ordenar(pendientes)

    def listar_vencidas(self) -> list:
        return [t for t in self._tareas if t.esta_vencida()]

    @medir_tiempo
    def guardar(self, archivo: str = ARCHIVO_DATOS) -> None:
        datos = {
            "comparador": (
                "fecha"
                if isinstance(self._comparador, ComparadorPorFechaVencimiento)
                else "prioridad"
            ),
            "tareas": [_tarea_a_dict(t) for t in self._tareas],
        }
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def cargar(self, archivo: str = ARCHIVO_DATOS) -> bool:
        if not os.path.exists(archivo):
            return False
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        self._tareas = []
        for d in datos.get("tareas", []):
            self._tareas.append(_tarea_desde_dict(d, self))

        if datos.get("comparador") == "fecha":
            self._comparador = ComparadorPorFechaVencimiento()
        else:
            self._comparador = ComparadorPorPrioridad()
        return True


# =============================================================================
# INTERFAZ DE CONSOLA
# =============================================================================

def pedir_fecha(mensaje: str) -> date:
    while True:
        texto = input(c(f"  {mensaje}", Color.ROJO)).strip()
        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            print(c("Formato inválido. Usá AAAA-MM-DD (ej: 2026-07-01).", Color.ROJO))


def pedir_prioridad() -> Prioridad:
    print(c("  Prioridad:", Color.BOLD))
    print(f"    {c('1)', Color.VERDE)} Baja   {c('2)', Color.AMARILLO)} Media   {c('3)', Color.ROJO)} Alta")
    opcion = input(c("  Elegí una opción [2]: ", Color.MAGENTA)).strip() or "2"
    return {"1": Prioridad.BAJA, "2": Prioridad.MEDIA, "3": Prioridad.ALTA}.get(
        opcion, Prioridad.MEDIA
    )


def pedir_id(mensaje: str) -> int:
    while True:
        texto = input(c(f"  {mensaje}", Color.AZUL)).strip()
        if texto.isdigit():
            return int(texto)
        print(c("Ingresá un número de ID válido.", Color.AZUL))


@encabezado("Nueva tarea")
@validar_titulo
def agregar_tarea_simple(gestor: GestorDeTareas) -> None:
    titulo = input(c("  Título: ", Color.AZUL)).strip()
    while not titulo:
        print(c(" El título no puede estar vacío.", Color.ROJO))
        titulo = input(c("  Título: ", Color.ROJO)).strip()
    fecha      = pedir_fecha("Fecha de vencimiento (AAAA-MM-DD): ")
    prioridad  = pedir_prioridad()
    nombre_cat = input(c("  Categoría (vacío = sin categoría): ", Color.AZUL)).strip()
    categoria  = gestor.obtener_o_crear_categoria(nombre_cat) if nombre_cat else None
    notas      = input(c("  Notas (opcional): ", Color.AZUL)).strip()
    tarea      = TareaSimple(titulo, fecha, prioridad, categoria, notas)
    gestor.agregar_tarea(tarea)
    print(c(f"\n Tarea creada:", Color.VERDE))
    print(tarea)


@encabezado("Nueva tarea recurrente")
def agregar_tarea_recurrente(gestor: GestorDeTareas) -> None:
    titulo = input(c("  Título: ", Color.AZUL)).strip()
    while not titulo:
        print(c(" El título no puede estar vacío.", Color.ROJO))
        titulo = input(c("  Título: ", Color.ROJO)).strip()
    fecha      = pedir_fecha("Próxima fecha (AAAA-MM-DD): ")
    frec_txt   = input(c("  Frecuencia en días [7]: ", Color.ROJO)).strip() or "7"
    frecuencia = int(frec_txt)
    prioridad  = pedir_prioridad()
    nombre_cat = input(c("  Categoría (vacío = sin categoría): ", Color.ROJO)).strip()
    categoria  = gestor.obtener_o_crear_categoria(nombre_cat) if nombre_cat else None
    tarea      = TareaRecurrente(titulo, fecha, frecuencia, prioridad, categoria)
    gestor.agregar_tarea(tarea)
    print(c(f"\n Tarea creada:", Color.VERDE))
    print(tarea)


@encabezado("Tareas")
@separador
def listar(tareas: list) -> None:
    if not tareas:
        print(c("  (No hay tareas para mostrar)", Color.DIM))
        return
    for tarea in tareas:
        print(tarea)


# -----------------------------------------------------------------------------
# NUEVO: Ver detalle completo de una tarea (incluyendo notas/cuerpo)
# -----------------------------------------------------------------------------

@encabezado("Detalle de tarea")
def ver_detalle_tarea(gestor: GestorDeTareas) -> None:
    # Primero mostramos el listado para que el usuario vea los IDs disponibles
    tareas = gestor.listar_tareas()
    if not tareas:
        print(c("  (No hay tareas cargadas)", Color.DIM))
        return

    for tarea in tareas:
        print(tarea)

    print()
    tarea = gestor.buscar_tarea(pedir_id("ID de la tarea a ver: "))

    if tarea is None:
        print(c("  No se encontró una tarea con ese ID.", Color.ROJO))
        return

    ancho  = 50
    borde  = c("│", Color.AZUL)
    tope   = c("┌" + "─" * ancho + "┐", Color.AZUL)
    fondo  = c("└" + "─" * ancho + "┘", Color.AZUL)

    def fila_dato(etiqueta: str, valor: str) -> None:
        etiq_str = c(f"{etiqueta:<16}", Color.DIM)
        pad = max(0, ancho - 2 - 16 - 1 - len_visible(valor))
        print(f"{borde}  {etiq_str} {valor}{' ' * pad}{borde}")

    print(f"\n{tope}")

    # Título
    titulo_visible = tarea.titulo
    pad = max(0, ancho - 2 - len(titulo_visible))
    print(f"{borde}  {c(titulo_visible, Color.BOLD, Color.AZUL)}{' ' * pad}{borde}")
    print(c("│" + "─" * ancho + "│", Color.AZUL))

    # Tipo de tarea
    tipo = "Recurrente" if isinstance(tarea, TareaRecurrente) else "Simple"
    fila_dato("Tipo:", tipo)

    # Categoría
    cat_str = str(tarea.categoria) if tarea.categoria else c("(sin categoría)", Color.DIM)
    fila_dato("Categoría:", cat_str)

    # Estado
    ico_e = tarea.estado.icono()
    est_str = c(f"{ico_e} {tarea.estado}", tarea.estado.color())
    fila_dato("Estado:", est_str)

    # Prioridad
    ico_p = tarea.prioridad.icono()
    prio_str = c(f"{ico_p} {tarea.prioridad}", tarea.prioridad.color())
    fila_dato("Prioridad:", prio_str)

    # Fecha de vencimiento / próxima
    etiq_fecha = "Próxima fecha:" if isinstance(tarea, TareaRecurrente) else "Vence:"
    vencida_tag = c("  ⚠ VENCIDA", Color.BOLD, Color.BG_MAGENTA, Color.BLANCO) if tarea.esta_vencida() else ""
    fila_dato(etiq_fecha, c(str(tarea.fecha_vencimiento), Color.ROJO) + vencida_tag)

    # Frecuencia (solo recurrentes)
    if isinstance(tarea, TareaRecurrente):
        fila_dato("Frecuencia:", c(f"cada {tarea.frecuencia_dias} días", Color.MAGENTA))

    # Notas (solo tareas simples — el "cuerpo" que pedías ver)
    if isinstance(tarea, TareaSimple):
        print(c("│" + "─" * ancho + "│", Color.AZUL))
        fila_dato("Notas:", "")
        notas = tarea.notas if tarea.notas else c("(sin notas)", Color.DIM)
        # Dividimos las notas en líneas de hasta (ancho-4) caracteres
        max_chars = ancho - 4
        palabras  = notas.split()
        linea_actual = ""
        lineas_notas = []
        for palabra in palabras:
            if len(linea_actual) + len(palabra) + 1 <= max_chars:
                linea_actual += ("" if not linea_actual else " ") + palabra
            else:
                if linea_actual:
                    lineas_notas.append(linea_actual)
                linea_actual = palabra
        if linea_actual:
            lineas_notas.append(linea_actual)

        for ln in lineas_notas:
            pad = ancho - 4 - len(ln)
            print(f"{borde}    {ln}{' ' * pad}{borde}")

    print(fondo)


# -----------------------------------------------------------------------------

@encabezado("Criterio de orden")
def cambiar_criterio(gestor: GestorDeTareas) -> None:
    print(f"  {c('1', Color.BOLD)} Por prioridad   {c('2', Color.BOLD)} Por fecha de vencimiento")
    opcion = input(c(" Elegí una opción: ", Color.ROJO)).strip()
    if opcion == "2":
        gestor.establecer_comparador(ComparadorPorFechaVencimiento())
        print(c("Orden actualizado: por fecha de vencimiento.", Color.VERDE))
    else:
        gestor.establecer_comparador(ComparadorPorPrioridad())
        print(c("Orden actualizado: por prioridad.", Color.VERDE))


def cargar_datos_ejemplo(gestor: GestorDeTareas) -> None:
    trabajo  = gestor.obtener_o_crear_categoria("Trabajo",  "azul")
    personal = gestor.obtener_o_crear_categoria("Personal", "verde")
    gestor.agregar_tarea(
        TareaSimple("Entregar informe mensual", date(2026, 6, 25), Prioridad.ALTA, trabajo,
                    "Incluir las métricas de Q2 y el comparativo con el año anterior.")
    )
    gestor.agregar_tarea(
        TareaSimple("Comprar regalo de cumpleaños", date(2026, 6, 21), Prioridad.MEDIA, personal,
                    "Regalo para María. Le gustan los libros de ciencia ficción y el café.")
    )
    gestor.agregar_tarea(
        TareaSimple("Renovar el carnet", date(2026, 5, 1), Prioridad.BAJA, personal,
                    "Llevar DNI, fotocopia y comprobante de domicilio. Turno: 10:30hs.")
    )


def mostrar_menu() -> None:
    ancho = 40
    borde = c("║", Color.ROJO)
    tope  = c("╔" + "═" * ancho + "╗", Color.ROJO)
    fondo = c("╚" + "═" * ancho + "╝", Color.ROJO)

    def fila(txt: str) -> str:
        interior = txt.ljust(ancho)
        return f"{borde}{interior}{borde}"

    opciones = [
        ("1",  "Agregar tarea simple"),
        ("2",  "Agregar tarea recurrente"),
        ("3",  "Listar todas las tareas"),
        ("4",  "Listar tareas pendientes"),
        ("5",  "Listar tareas vencidas"),
        ("6",  "Ver detalle / notas de una tarea"),   # ← NUEVA OPCIÓN
        ("7",  "Marcar tarea como completada"),
        ("8",  "Eliminar tarea"),
        ("9",  "Cambiar criterio de orden"),
        ("10", "Salir"),
    ]

    print(f"\n{tope}")
    titulo_centrado = "GESTOR DE TAREAS".center(ancho)
    print(fila(c(titulo_centrado, Color.BOLD, Color.AZUL)))
    print(c("║" + "─" * ancho + "║", Color.ROJO))
    for num, desc in opciones:
        linea = f"  {c(num, Color.BOLD, Color.AZUL)}) {desc}"
        padding = ancho - len(f"  {num}) {desc}")
        print(f"{borde}{linea}{' ' * padding}{borde}")
    print(fondo)


@confirmacion_guardado
def _guardar(gestor: GestorDeTareas) -> None:
    gestor.guardar()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    gestor = GestorDeTareas.obtener_instancia()

    if gestor.cargar():
        print(c(f"\n Tareas cargadas desde '{ARCHIVO_DATOS}'.", Color.VERDE))
    else:
        cargar_datos_ejemplo(gestor)
        print(c("\n No había datos guardados: se cargaron tareas de ejemplo.", Color.AMARILLO))

    while True:
        mostrar_menu()
        opcion = input(c("\n Elegí una opción: ", Color.BOLD, Color.AZUL)).strip()

        if opcion == "1":
            agregar_tarea_simple(gestor)
            _guardar(gestor)
        elif opcion == "2":
            agregar_tarea_recurrente(gestor)
            _guardar(gestor)
        elif opcion == "3":
            listar(gestor.listar_tareas())
        elif opcion == "4":
            listar(gestor.listar_pendientes())
        elif opcion == "5":
            listar(gestor.listar_vencidas())
            _guardar(gestor)
        elif opcion == "6":                          # ← NUEVA OPCIÓN
            ver_detalle_tarea(gestor)
        elif opcion == "7":
            tarea = gestor.buscar_tarea(pedir_id("ID de la tarea a completar: "))
            if tarea:
                tarea.marcar_completada()
                _guardar(gestor)
                print(c("Tarea marcada como completada.", Color.VERDE))
            else:
                print(c("No se encontró esa tarea.", Color.ROJO))
        elif opcion == "8":
            if gestor.eliminar_tarea(pedir_id("ID de la tarea a eliminar: ")):
                _guardar(gestor)
                print(c("Tarea eliminada.", Color.VERDE))
            else:
                print(c("No se encontró esa tarea.", Color.ROJO))
        elif opcion == "9":
            cambiar_criterio(gestor)
            _guardar(gestor)
        elif opcion == "10":
            _guardar(gestor)
            print(c("\n  ¡Hasta la próxima!\n", Color.BOLD, Color.ROJO))
            break
        else:
            print(c("Opción inválida.", Color.ROJO))


if __name__ == "__main__":
    main()
