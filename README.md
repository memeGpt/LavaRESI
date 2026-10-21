# LavaRESI — Sistema Inteligente de Gestión de Lavandería

## Descripción

**LavaRESI** es un proyecto universitario desarrollado para el curso de Paradigmas de Programación. Su objetivo es gestionar el uso de una lavandería mediante una terminal física y una aplicación web, permitiendo organizar turnos, controlar ciclos de lavado y secado, y administrar las tandas de ropa de los estudiantes.

El prototipo contempla una lavadora y una secadora que funcionan de manera independiente.

## Funcionalidades principales

- Registro e identificación de estudiantes mediante PIN.
- Solicitud de turnos para lavadora y secadora.
- Registro de 1 a 3 tandas por solicitud.
- Administración de colas y prioridades.
- Gestión de disponibilidad de los estudiantes.
- Inicio de ciclos con temporizadores independientes.
- Confirmación del retiro de ropa.
- Consulta de turnos desde la terminal y la página web.
- Indicadores LED y alertas sonoras para los estados de las máquinas.

## Tecnologías

| Componente | Tecnología |
|---|---|
| Terminal física | ESP32 y Arduino UNO (C++) |
| Pantalla | LCD 16×2 con comunicación I2C |
| Backend | Python + FastAPI (propuesto) |
| Frontend | HTML, CSS y JavaScript (propuesto) |
| Base de datos | SQLite (propuesto) |
| Lógica de prioridades | SWI-Prolog |
| Modelo físico | Diseño e impresión 3D |
| Control de versiones | Git y GitHub |

## Estructura del proyecto

```text
LavaRESI/
├── bitacoras/          # Registro de avances
├── documentacion/      # Arquitectura, evidencias y manuales
├── hardware/           # Código del ESP32, Arduino y conexiones
├── software/
│   ├── backend/        # API, base de datos y Prolog
│   └── frontend/       # Aplicación web
├── modelo-3d/          # Diseño de la carcasa
└── README.md
```

## Funcionamiento general

1. El estudiante se identifica mediante su PIN.
2. Selecciona una máquina y registra la cantidad de tandas.
3. LavaRESI organiza las solicitudes según el orden de llegada y la disponibilidad.
4. Cuando le corresponde, el estudiante inicia su ciclo desde la terminal física.
5. Al finalizar, el sistema activa una alerta y solicita confirmar el retiro de la ropa.
6. El turno se mantiene hasta completar todas las tandas registradas y liberar la máquina.

Las reglas de prioridad se implementan mediante Prolog, mientras el backend centraliza la información compartida entre la terminal y la página web.

## Estado del proyecto

Actualmente se ha desarrollado y probado la terminal física, incluyendo la LCD, el joystick, el control infrarrojo, los seis indicadores LED, el buzzer y los temporizadores independientes.

Se encuentra en desarrollo la integración con el backend, la base de datos, Prolog, la aplicación web y el modelo 3D.

## Equipo de desarrollo

Proyecto desarrollado por estudiantes universitarios como parte del curso de **Paradigmas de Programación**.