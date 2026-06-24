Sistema de Gestión de Tareas Personales — TPI

Aplicación de consola en Python (un solo archivo) que modela un gestor de tareas personales, aplicando POO, diseño orientado a objetos y patrones de diseño.

Menú interactivo

--- Gestor de tareas personales ---
1) Agregar tarea simple
2) Agregar tarea recurrente
3) Listar todas las tareas
4) Listar tareas pendientes
5) Listar tareas vencidas
6) Marcar tarea como completada
7) Eliminar tarea
8) Cambiar criterio de orden
9) Salir

#Conceptos de POO aplicados


-Encapsulamiento: Todos los atributos son privados (_atributo) y se exponen mediante propiedades (@property) de solo lectura. El estado solo cambia a través de métodos explícitos (marcar_completada(), reprogramar(), etc.), nunca asignando directamente.
-Abstracción: Tarea y ComparadorTareas son clases abstractas (ABC) que definen un contrato (esta_vencida(), obtener_resumen(), comparar()) sin implementarlo del todo, dejando los detalles a cargo de las subclases concretas.
-Herencia: TareaSimple y TareaRecurrente heredan de Tarea. ComparadorPorPrioridad y ComparadorPorFechaVencimiento heredan de ComparadorTareas.

-Polimorfismo: el mismo mensaje produce comportamientos distintos según la clase concreta que lo recibe:
1) esta_vencida(): Una TareaSimple queda marcada como vencida si pasó su fecha límite; una TareaRecurrente, en cambio, nunca queda "vencida": se reprograma automáticamente para la próxima fecha.
2) obtener_resumen(): cada subclase de Tarea arma su propia descripción de texto.
3) comparar(): cada ComparadorTareas define un criterio de orden distinto (prioridad vs. fecha de vencimiento).

##Relaciones entre objetos

-Composición: GestorDeTareas contiene y es responsable del ciclo de vida de sus Tarea — si se elimina una tarea del gestor, deja de existir en el sistema.
-Agregación: Tarea referencia a una Categoria, pero la categoría existe de forma independiente y puede ser compartida por varias tareas a la vez (el gestor las administra en un diccionario propio).
-Dependencia: Tarea usa los enumerados Prioridad y EstadoTarea para representar su estado interno.


##Patrones de diseño aplicados

-Singleton (GestorDeTareas): garantiza una única instancia global que centraliza todas las tareas y categorías del sistema. Se implementa sobreescribiendo __new__(), y se expone además a través de obtener_instancia().
-Strategy (ComparadorTareas, ComparadorPorPrioridad, ComparadorPorFechaVencimiento): GestorDeTareas delega el criterio de orden de las tareas en un objeto ComparadorTareas intercambiable en tiempo de ejecución (establecer_comparador()), sin necesidad de modificar el gestor para agregar un nuevo criterio (principio abierto/cerrado).

