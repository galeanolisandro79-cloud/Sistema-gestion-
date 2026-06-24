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
