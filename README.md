# Sistema de Gestión de Turnos (Clínica médica) — TPI

Aplicación de consola en Python que modela el agendamiento de turnos en
una clínica médica, aplicando POO, diseño orientado a objetos, patrones
de diseño y modelado UML.


La aplicación es **interactiva**: muestra un menú numerado y el usuario va
ingresando los datos por teclado. No hay una demo fija — cada
ejecución depende de lo que el usuario decida hacer.


--

==================================================
   SISTEMA DE GESTIÓN DE TURNOS - CLÍNICA
==================================================
1) Registrarme como paciente
2) Ver especialistas disponibles
3) Sacar un turno
4) Confirmar turno
5) Cancelar turno
6) Ver turnos de un especialista
7) Ver todos los turnos
0) Salir
--------------------------------------------------
Elija una opción:
``

Flujo típico para probarlo en la exposición:
1. Ver los especialistas disponibles (ya precargados con matrícula).
2. Registrarse como paciente.
3. Sacar un turno con alguno de los especialistas (tipo presencial, virtual
   o urgencia, y canal de notificación: email o SMS).
4. Confirmarlo y ver cómo dispara el aviso por el canal elegido (Strategy).
5. Probar cancelar un turno o ver la agenda de un especialista.


## Conceptos de POO aplicados

- **Encapsulamiento**: atributos privados ("_atributo") expuestos mediante
  propiedades de solo lectura, con métodos específicos para mutar estado
  ("confirmar()", "cancelar()") en lugar de setters libres.
- **Abstracción**: "Persona" y "Turno" son clases abstractas ("ABC") que
  definen el contrato común sin implementación concreta de "describir()",
  "calcular_duracion_minutos()" y "mostrar_info()".
- **Herencia**:
  - "Paciente" y "Profesional" heredan de "Persona".
  - "TurnoPresencial", "TurnoVirtual" y "TurnoUrgencia" heredan de "Turno".
- **Polimorfismo**: el mismo mensaje ("mostrar_info()",
  "calcular_duracion_minutos()") produce comportamientos distintos según
  la clase concreta. En "main.py", el ciclo que recorre los turnos de un
  profesional no necesita saber si cada turno es presencial, virtual o
  de urgencia.

## Relaciones entre objetos

- **Asociación**: "Turno" referencia a un "Paciente" y a un "Profesional",
  sin ser propietario exclusivo de ninguno de los dos.
- **Agregación**: "Clinica" agrega "Paciente" y "Profesional" (podrían
  existir conceptualmente fuera de esta clínica puntual).
- **Composición**: "Clinica" compone los "Turno": cada turno es
  administrado íntegramente por la clínica que lo agendó.

## Patrones de diseño aplicados

1. **Singleton** ("Clinica"): garantiza una única instancia del sistema
   central que coordina pacientes, profesionales y turnos. Se implementa
   sobreescribiendo "__new__".
2. **Factory Method** ("TurnoFactory"): centraliza la creación de
   "TurnoPresencial", "TurnoVirtual" y "TurnoUrgencia" a través de un
   único método "crear_turno(tipo, ...)", evitando que el código cliente
   dependa de las clases concretas.
3. **Strategy** ("INotificacionStrategy", "EmailNotificacionStrategy",
   `SmsNotificacionStrategy"): cada "Turno" delega en una estrategia el
   "cómo" recordarle al paciente su turno. La estrategia se puede definir
   al crear el turno o cambiarse dinámicamente con
   "cambiar_estrategia_notificacion()" , sin tocar la clase "Turno".

## Diagrama de clases

El archivo "diagrama_clases.mermaid" contiene el diagrama UML completo
(clases, atributos, métodos, herencia, interfaces y relaciones). Se puede
visualizar pegando su contenido en https://mermaid.live o en cualquier
editor compatible con Mermaid (VS Code, GitHub, Notion, etc.).

## Datos precargados

Al iniciar, la clínica ya tiene un plantel de especialistas con matrículas
de ejemplo (ver "cargar_especialistas_iniciales()" en "main.py"):

| Especialista | Especialidad | Matrícula |
|---|---|---|
| Carla Ibáñez | Cardiología | MN-12345 |
| Martín Suárez | Pediatría | MN-23456 |
| Laura Paredes | Dermatología | MN-34567 |
| Diego Fernández | Traumatología | MN-45678 |
| Valeria Castro | Ginecología | MN-56789 |

Los pacientes **no dan de alta especialistas**: se registran ellos mismos
y sacan turno directamente eligiendo entre los ya disponibles.

## Opciones del menú interactivo

| Opción | Acción |
|---|---|
| 1 | Registrarse como "Paciente" |
| 2 | Ver el listado de especialistas ("Profesional") disponibles |
| 3 | Sacar un "Turno" con un especialista (elige tipo, fecha/hora y canal de notificación) usando "TurnoFactory" |
| 4 | Confirmar un turno existente — dispara la notificación vía la "INotificacionStrategy" configurada |
| 5 | Cancelar un turno existente |
| 6 | Ver todos los turnos de un especialista puntual |
| 7 | Ver todos los turnos agendados en el sistema |
| 0 | Salir |

Toda la lógica de negocio (validaciones, creación de objetos, cálculo de
duración, notificación) vive en las clases de "models/" y en "Clinica";
"main.py" solo se ocupa de precargar datos, pedir información por consola
y mostrar resultados.
