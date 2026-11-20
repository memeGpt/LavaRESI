Bitácora de trabajo individual — LavaRESI
Integrante: Melissa Tijerino Espinoza
Proyecto: LavaRESI — Sistema de gestión de turnos para lavadora y secadora
Periodo documentado: octubre y noviembre de 2026
Última actualización:  16 de noviembre de 2026
Tipo de proyecto: Desarrollo colaborativo, con integración de hardware, backend y aplicación web.
1. Objetivo de mi trabajo
Participar en el desarrollo y las pruebas de LavaRESI, especialmente en la integración de la terminal física con la página web y el backend. Mi trabajo se centró en verificar el funcionamiento de los componentes electrónicos, adaptar las consultas y operaciones del ESP32 al sistema de turnos real, revisar el comportamiento de las colas y mejorar la experiencia de uso de la interfaz web.
Esta bitácora registra mis actividades y pruebas dentro del proyecto en equipo. No atribuye a una sola persona el desarrollo completo de LavaRESI. Las fechas agrupan los avances documentados y algunas actividades se realizaron en varias sesiones.

2. Registro cronológico de actividades
17 de octubre de 2026 — Comunicación entre ESP32, Arduino UNO y LCD
Actividades realizadas:
- Probé la comunicación del ESP32 con el Arduino UNO para mostrar información en la pantalla LCD de 16 × 2.
- Verifiqué la LCD con módulo I2C, dirección 0x27, conectada al UNO mediante SDA (A4) y SCL (A5).
- Revisé la visualización de mensajes del sistema: espera, inicio de tanda, tiempo restante, finalización y retiro de ropa.
- Conservé la solución con Arduino UNO y LCD, debido a los problemas de estabilidad que se habían presentado al intentar usar otra pantalla.
Resultado: Se consiguió presentar información del sistema en la LCD mediante la comunicación entre las dos placas.
19 y 20 de octubre de 2026 — Controles y navegación física
Actividades realizadas:
- Conecté y probé el joystick para navegar entre Lavadora, Secadora y Consultas.
- Probé el receptor infrarrojo y el control remoto para desplazarse por los menús, confirmar opciones e ingresar valores numéricos.
- Realicé pruebas del buzzer activo controlado desde el ESP32 mediante un transistor PN2222A.
- Revisé las pantallas de ingreso de PIN, selección de 1 a 3 tandas, consulta de posición y menú «Mi turno».
- Probé la lógica de continuar con otra tanda y liberar la máquina después del retiro final en las versiones iniciales del programa.
Resultado: La terminal física permitió interactuar con los menús y ejecutar pruebas de turnos mediante joystick, control remoto y LCD.
Finales de octubre de 2026 — Preparación de la integración del sistema
Actividades realizadas:
- Revisé los requisitos para que la terminal ESP32 y la página web utilizaran el mismo estado de turnos, en lugar de mantener colas de demostración independientes.
- Participé en la integración de la arquitectura que utiliza FastAPI como backend, PostgreSQL en Neon para los registros y Prolog para las reglas de asignación y disponibilidad.
- Trabajé sobre las rutas y servicios necesarios para consultar máquinas, identificar al estudiante por PIN, registrar solicitudes e iniciar o retirar tandas.
Resultado: Quedó definida y desarrollada progresivamente la comunicación entre los módulos del sistema.
Primera semana de noviembre de 2026 — Cambios en backend y página web
Actividades realizadas:
- Modifiqué y probé archivos de software/backend/app/ relacionados con las rutas públicas, web y terminal, y con los servicios de turnos y Prolog.
- Integré actualizaciones mediante WebSocket para que la interfaz pudiera recibir cambios de estado sin recargar toda la página.
- Trabajé en software/frontend/index.html, css/estilos.css y js/app.js para organizar el inicio de sesión, el estado de las máquinas, la solicitud de turnos y las consultas del estudiante.
- Comprobé que la información pública mostrara la disponibilidad de las máquinas sin exponer nombres de integrantes de las colas.
- Revisé las respuestas de FastAPI (/api/estado, /api/yo) y el funcionamiento de la sesión al entrar y salir de la web.
Resultado: La web y el backend pudieron mostrar los estados registrados en la base de datos; se identificaron y corrigieron problemas de carga y visualización de la sesión.
9 de noviembre de 2026 — Pruebas reales de colas y autorización
Actividades realizadas:
- Realicé pruebas de los turnos con registros de estudiantes existentes en la base de datos.
- Detecté que una solicitud anterior de Justin impedía a Grace iniciar un ciclo de lavadora.
- Cancelé la solicitud de prueba correspondiente y comprobé que Grace pasó al primer puesto; después revisé la necesidad de recalcular la autorización del siguiente turno.
- Identifiqué que la LCD mostraba «Sin espera» aun cuando la base de datos tenía solicitudes: el ESP32 estaba recibiendo la respuesta pública de /api/estado, sin la lista privada.
- Ajusté la consulta autenticada de la terminal mediante la clave correspondiente y repetí las pruebas.
- Confirmé que la LCD llegó a mostrar Grace en la cola de lavadora y Jareth en la cola de secadora.
Resultado: Se corrigió la diferencia entre las colas del backend y su visualización en la terminal física. Además, se verificó que el PIN y la posición del estudiante podían consultarse desde el ESP32.
9 al 11 de noviembre de 2026 — Pruebas de ciclos, reloj y avisos sonoros
Actividades realizadas:
- Probé el inicio de una tanda de un minuto desde la terminal física, utilizando un turno autorizado.
- Comprobé que el sistema pasaba a la pantalla de minutos y podía iniciar el ciclo.
- Detecté que el tiempo visible comenzaba con varios segundos menos, porque la terminal realizaba consultas al servidor antes de actualizar la LCD.
- Identifiqué un problema con el buzzer: los pitidos de inicio y retiro podían durar demasiado cuando coincidían con una solicitud HTTP.
- Revisé versiones del programa para separar el control del buzzer de las consultas al backend y establecer la secuencia acordada: dos pitidos al iniciar, tres al finalizar y dos al retirar.
- Revisé la pantalla «Mi turno» porque inicialmente abría la consulta de lavadora, incluso cuando el estudiante tenía una solicitud activa de secadora pendiente de retiro.
Resultado: Se documentaron los errores encontrados durante la prueba integrada y se prepararon correcciones del ESP32. La validación física definitiva de estas correcciones debe realizarse con la versión efectivamente cargada en la placa.
13 de noviembre de 2026 — Documentación y coordinación con el equipo
Actividades realizadas:
- Preparé una guía de instalación y pruebas de LavaRESI para que un compañero pudiera configurar Arduino IDE y probar la parte física junto con la web.
- Documenté la instalación del soporte ESP32 by Espressif Systems y las bibliotecas IRremote y ArduinoJson 7.x, además de la configuración necesaria para el Arduino UNO y la LCD.
- Organicé los cambios de backend, frontend, reglas Prolog, pruebas y hardware para compartirlos mediante GitHub.
- Revisé el uso de git status, git add, git commit y git push para preparar la entrega al repositorio del equipo.
Resultado: Se facilitó la reproducción de las pruebas en otra computadora. La publicación final de cada cambio debe comprobarse en GitHub después del push.
17 de noviembre de 2026 — Verificación del cableado
Actividades realizadas:
- Revisé nuevamente las conexiones del joystick, receptor IR, RGB de lavadora y secadora, buzzer, Arduino UNO y LCD.
- Contrasté los GPIO utilizados con el programa del ESP32, sin modificar el cableado que ya se había probado.
- Verifiqué especialmente las señales del joystick (32, 35, 25), el receptor IR (34), los RGB (18, 19, 22, 23), el buzzer (26) y la comunicación con el UNO (17 hacia D2).
Resultado: Quedó documentada la asignación de pines para apoyar las pruebas físicas del equipo.
3. Archivos y módulos en los que trabajé
Área	Archivos o componentes	Trabajo realizado
ESP32	hardware/esp32	Menús, lectura de PIN, consulta de colas y estado, inicio/retiro de tandas, LCD, temporización, RGB y buzzer.
Backend	software/backend/app/main.py	Integración del servidor y actualizaciones de estado.
Rutas	software/backend/app/rutas/publico.py, web.py, terminal.py, eventos.py	Consultas públicas/privadas, operaciones del estudiante y notificaciones por WebSocket.
Lógica de turnos	software/backend/app/servicios/turnos.py, prolog.py	Revisión de autorización, posiciones y disponibilidad.
Reglas	software/backend/prolog/reglas_turnos.pl	Revisión y pruebas de las reglas utilizadas para los turnos.
Pruebas	software/backend/tests/test_prioridad.py	Pruebas de prioridad y disponibilidad.
Frontend	software/frontend/index.html, css/estilos.css, js/app.js	Inicio de sesión, consultas de máquinas y turnos, ajustes visuales y actualización dinámica.


4. Principales dificultades y soluciones
Dificultad	Acción realizada / aprendizaje
La LCD mostraba una cola vacía, aunque existían solicitudes.	Se identificó la diferencia entre la respuesta pública y la privada de la API y se ajustó la autenticación del ESP32.
Una solicitud anterior impedía iniciar el lavado.	Se revisó la cola de prueba y la reasignación de la autorización del siguiente estudiante.
La web parecía parpadear o cambiar de pantalla al cargar la sesión.	Se revisaron la consulta de sesión, la carga de JavaScript y la visibilidad inicial del formulario.
El buzzer emitía sonidos demasiado largos.	Se identificó que las consultas bloqueantes interferían con el apagado del buzzer; se preparó su ejecución independiente.
La pantalla «Mi turno» priorizaba siempre la lavadora.	Se revisó el flujo para contemplar solicitudes de cualquiera de las dos máquinas y estados pendientes de retiro.
El cronómetro no se mostraba inmediatamente después de iniciar.	Se revisó el orden de consultas y la visualización local del tiempo recibido del servidor.


5. Pruebas y evidencias disponibles
- Mensajes del Monitor Serial del ESP32 con HTTP 200 al consultar /api/estado.
- Registros de FastAPI con respuestas de /api/estado, /api/yo, autenticación y conexión WebSocket.
- Pruebas con cuentas registradas para consultar posición y confirmar turnos en lavadora y secadora.
- Observación de una tanda de un minuto, la cuenta regresiva y los avisos de finalización.
- Capturas de la página web y de los problemas de interfaz detectados durante las pruebas.
- Guía de instalación para reproducir las pruebas físicas con otro integrante del equipo.
6. Aspectos pendientes de validación
1. Confirmar con el compañero que la última versión del programa ESP32 compila y funciona en el montaje real.
2. Verificar físicamente que los avisos suenen como 2 / 3 / 2 pitidos cortos, sin alargarse durante las consultas HTTP.
3. Confirmar que «Mi turno» identifica correctamente solicitudes en lavadora y secadora, incluidos los casos de retiro pendiente.
4. Comprobar la sincronización completa entre página web, backend, base de datos y terminal al iniciar, finalizar y retirar una tanda.
5. Revisar en GitHub que las actualizaciones del ESP32 estén incluidas; si hardware/esp32 es un submódulo, sus cambios pueden requerir una publicación independiente.
7. Reflexión personal
Durante este proyecto aprendí que integrar hardware y software requiere comprobar no solo que cada componente funcione por separado, sino que todos utilicen la misma información y respeten las mismas reglas. Una de las dificultades más importantes fue detectar que un HTTP 200 no garantiza que la terminal reciba todos los datos que necesita: también importa si la respuesta es pública o privada. Asimismo, las pruebas del buzzer y el temporizador me permitieron identificar cómo una consulta al servidor puede afectar el comportamiento físico cuando el programa no está organizado para evitar bloqueos.

Mi aporte se ha concentrado en conectar, probar, depurar y documentar el funcionamiento de LavaRESI para que sus componentes físicos y su interfaz web puedan utilizarse de manera coordinada.