---Gestor de Tareas Personales---

Aplicación de consola en Python para crear, organizar y dar seguimiento a tareas personales, con persistencia en un archivo JSON.

---Funcionalidades---

#Desde el menú interactivo se puede:

1) Agregar una tarea simple (fecha de vencimiento fija).
2) Agregar una tarea recurrente (se reprograma sola cada N días).
3) Listar todas las tareas.
4) Listar solo las pendientes (no vencidas ni completadas).
5) Listar las vencidas.
6) Marcar una tarea como completada.
7) Eliminar una tarea.
8) Cambiar el criterio de orden (por prioridad o por fecha de vencimiento).
9) Salir (guardando los cambios).

---Estructura del modelo---

--Clase--
-Tarea: Clase abstracta base. Define el contrato común (id, título, fechas, prioridad, estado, categoría) y dos métodos abstractos: esta_vencida() y obtener_resumen().
-TareaSimple: Tarea de una sola vez. Queda VENCIDA si pasó la fecha límite y no se completó.
-TareaRecurrente: Tarea periódica. En vez de vencerse, se reprograma sola sumando frecuencia_dias a su fecha de vencimiento.
-Categoria: Etiqueta liviana (nombre + color) que puede asignarse a cualquier tarea. Existe independientemente de las tareas que la usan.
-Prioridad/EstadoTarea: Enumeraciones (Baja/Media/Alta y Pendiente/En progreso/Completada).
-ComparadorTareasClase abstracta que define la interfaz de comparación (patrón Strategy).
-ComparadorPorPrioridad/ComparadorPorFechaVencimiento: Estrategias concretas de orden, intercambiables en tiempo de ejecución.
-GestorDeTareas: Único punto de acceso al sistema (patrón Singleton). Contiene las tareas, administra las categorías, aplica el comparador activo y maneja la persistencia en JSON.


---Conceptos de POO aplicados---

-Encapsulamiento: todos los atributos son privados (_atributo) y se exponen únicamente a través de @property.
-Abstracción: Tarea y ComparadorTareas son clases abstractas (ABC) que no se instancian directamente.
-Herencia: TareaSimple y TareaRecurrente heredan de Tarea; ComparadorPorPrioridad y ComparadorPorFechaVencimiento heredan de ComparadorTareas.
-Polimorfismo: esta_vencida(), obtener_resumen() y comparar() se comportan de forma distinta según la subclase concreta que recibe el mensaje.


---Relaciones entre objetos---

-Composición: GestorDeTareas contiene y es responsable del ciclo de vida de sus Tarea (si se elimina el gestor, las tareas no existen por fuera de él).
-Agregación: Tarea referencia una Categoria, pero esta existe de forma independiente y puede ser compartida por varias tareas a la vez.


---Patrones de diseño---

-Singleton (GestorDeTareas): garantiza una única instancia global que centraliza el estado de la aplicación.
-Strategy (ComparadorTareas): permite cambiar el criterio de orden de las tareas en tiempo de ejecución sin modificar el código de GestorDeTareas (principio abierto/cerrado).


---Decoradores de Python---

Además de los patrones de diseño clásicos, el código usa decoradores de funciones (@decorador) para separar la lógica de negocio de los detalles de presentación en consola:
--Decorador--
-@encabezado(titulo): Imprime un título destacado antes de ejecutar la función (se usa en las pantallas del menú).
-@confirmacion_guardado: Muestra un mensaje de confirmación después de guardar cambios.
-@separador: Imprime una línea divisoria al final de un listado.
-@medir_tiempo: Mide cuánto tarda una operación (por ejemplo, guardar()) y avisa si tardó más de 10 ms.
-@validar_titulo: Punto de extensión para validar que el título no esté vacío antes de crear una tarea.
Estos decoradores envuelven funciones como agregar_tarea_simple, listar o guardar, agregándoles comportamiento (encabezados, medición de tiempo, confirmaciones) sin modificar su lógica interna.


