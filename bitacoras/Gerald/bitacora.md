Bitácora individual de desarrollo — LavaRESI (artículo IEEE)


Estudiante
Gerald David Araya Jimenez
Curso
Paradigmas de programación EIF-400
Proyecto
LavaRESI — sistema de gestión de turnos para la lavandería de residencias estudiantiles mediante una terminal IoT y una aplicación web
Rol en el equipo
Redacción y revisión del artículo científico en formato IEEE
Período
17 de noviembre de 2026

1. Resumen de mi aporte
Me encargué de convertir el trabajo técnico de LavaRESI (terminal con ESP32 y Arduino UNO, servidor en Python con FastAPI, base de datos PostgreSQL, motor de reglas en Prolog y carcasa impresa en 3D) en un artículo que cumpla las normas IEEE. Mi trabajo cubrió todo el proceso:
• Análisis del código, la documentación y las bitácoras del equipo para escribir solo lo que el proyecto realmente hace.
• Redacción del artículo: resumen, introducción, diseño, funcionamiento, pruebas y conclusiones.
• Revisión del formato contra la guía de citación IEEE entregada en el curso.
• Búsqueda y verificación de las fuentes bibliográficas, y redacción de la sección de trabajos relacionados.
• Corrección final del documento en Word (figuras, tabla, referencias y maquetación a dos columnas).
2. Herramientas y tecnologías
Herramienta
Uso
Guía IEEE (PDF de la Revista Forestal Mesoamericana Kurú)
Reglas de citación en el texto y formato de la lista de referencias
Microsoft Word
Edición del artículo, autores, correos, figuras y tabla
Claude (asistente de IA de Anthropic)
Guía de apoyo: estructura del artículo, revisión contra la guía IEEE y verificación de fuentes.
MDPI, catálogos de bibliotecas y páginas de editoriales
Confirmar autores, año, editorial y contenido de cada fuente
Repositorio LavaRESI (código, bitácoras y pruebas)
Fuente de los datos técnicos del artículo
Relación con los paradigmas del curso
Al describir el sistema identifiqué cómo cada paradigma se refleja en el proyecto. El servidor y el firmware del ESP32 siguen un enfoque imperativo. La decisión de a quién le corresponde el turno es de programación lógica: el servidor envía a Prolog el estado de la máquina y las solicitudes, y las reglas responden con la decisión. El modelo de la carcasa en OpenSCAD es declarativo, porque un cambio en una variable se propaga a todas las piezas.
3. Estructura del artículo
Sección
Contenido
Resumen y palabras clave
Problema, solución y resultado en un párrafo
I. Introducción
Problema de las filas y la ropa olvidada, objetivo y paradigmas integrados
II. Trabajos relacionados
Proyectos IoT educativos con ESP32 y en qué se diferencia LavaRESI
III. Diseño del sistema
Arquitectura, terminal física, servidor y base de datos, motor de reglas, seguridad y carcasa 3D
IV. Funcionamiento
Registro e ingreso, cola de turnos, ausencias, ciclo y retiro de la ropa, estados de la máquina
V. Pruebas y resultados
14 pruebas automatizadas de prioridad y validación funcional de la terminal
VI. Conclusiones y trabajo futuro
Aportes, limitaciones y mejoras propuestas
Referencias
10 fuentes numeradas por orden de aparición
4. Registro cronológico
Fase 1 — Análisis del proyecto
17 de noviembre de 2026
Actividades
• Revisé el repositorio: los README, el esquema de la base de datos (5 tablas con sus restricciones), las reglas de Prolog, la lógica de turnos del servidor, la seguridad (contraseñas y PIN con hash PBKDF2, límite de intentos) y el código del ESP32.
• Leí las bitácoras del equipo y conté las pruebas automatizadas de prioridad (14).
Aprendizaje: el artículo debe describir lo que el sistema realmente hace, no solo lo que se recuerda de él.
Fase 2 — Primer borrador
Actividades
• Armé la estructura IMRyD adaptada al proyecto y redacté el resumen, la introducción, el diseño y el funcionamiento.
• Hice una tabla con los estados de la máquina (libre, en uso, pendiente de retiro y entre tandas) y sus colores de LED.
Decisiones
• No incluí métricas de reducción de tiempos de espera porque nunca se midieron. Lo dejé escrito como limitación y como trabajo futuro.
Fase 3 — Revisión contra la guía IEEE
Actividades
• Agregué los autores, correos y dos figuras al borrador en Word y revisé el archivo contra la guía.
Problemas encontrados y corregidos
• La referencia del estándar de contraseñas tenía pegado un texto de vista previa del enlace.
• La lista de referencias no tenía sangría ni separación entre entradas.
• Las Fig. 1 y Fig. 2 no se citaban en el texto, y sus leyendas y la de la tabla no seguían el formato IEEE.
• Los correos estaban unos con hipervínculo y otro sin él, y las imágenes no tenían texto alternativo.
• Pasé el documento a dos columnas con Times New Roman de 10 pt, justificado, y lo validé técnicamente.
Aprendizaje: revisar el formato tiene que hacerse contra la guía punto por punto, no a ojo.
Fase 4 — Trabajos relacionados y nuevas fuentes
Actividades
• Busqué y consulté cuatro fuentes: un artículo sobre dispositivos IoT con ESP32 (Hercog et al., 2023) y tres libros sobre FastAPI, PostgreSQL y Prolog.
• Agregué la sección II, Trabajos relacionados, y renumeré las demás secciones y las referencias para que sigan el orden de aparición.
Decisiones
• Usé el título original en inglés del artículo de Hercog et al., como pide IEEE, en lugar de su traducción.
• Quité el rango de páginas del libro de FastAPI, porque las partes que respaldan lo que digo están en otros capítulos.
Fase 5 — Verificación de referencias
Actividades
• Comprobé cada una de las 10 referencias contra fuentes externas y corregí tres errores:
    ◦ El estándar de contraseñas citado estaba obsoleto; lo cambié por su versión vigente (RFC 8018).
    ◦ Había puesto años que no estaban confirmados en páginas web sin fecha; usé "n.d." donde no hay año de publicación.
    ◦ Un enlace apuntaba a la página principal de Espressif en lugar de la hoja de datos.
• Agregué enlace y fecha de acceso a las referencias que no los tenían (libros y artículos).
• Hice una auditoría automática del archivo final: citas numeradas en orden, ninguna referencia sin citar ni cita sin referencia, y todas las fuentes web con enlace y fecha de acceso.
Problema encontrado
• Los enlaces de Google Books no se pueden abrir automáticamente, así que los armé con los identificadores de los enlaces originales y quedan por revisar a mano.
Aprendizaje: no se debe citar de memoria. Cada referencia hay que verificarla, y un estándar puede estar obsoleto aunque siga apareciendo en los buscadores.
5. Uso de herramientas de IA y verificación de originalidad
Usé Claude solo como guía de apoyo: estructura del artículo, revisión del formato IEEE y verificación de fuentes. Para verificar la originalidad, pasé el artículo por Turnitin, que revisa similitud y posible uso de IA, y el resultado fue inferior al 28 %.
