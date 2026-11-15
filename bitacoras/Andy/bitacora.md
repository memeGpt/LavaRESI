# Bitácora individual de desarrollo — LavaRESI

| | |
|---|---|
| **Estudiante** | Andy Alvarado Calderón|
| **Curso** | Paradigmas de programación EIF-400 |
| **Proyecto** | LavaRESI — prototipo IoT que muestra si la lavadora y la secadora de las residencias estudiantiles de la UNA están ocupadas o desocupadas |
| **Rol en el equipo** | Diseño y fabricación de la carcasa: modelado 3D, plantillas de calce e impresión 3D |
| **Período** | 5 de agosto de 2026 – 14 de noviembre de 2026 |
| **Repositorio** |  |

---

## 1. Resumen de mi aporte

Me encargué de convertir el prototipo electrónico de LavaRESI (ESP32, Arduino UNO, pantalla LCD 16x2 con I2C, joystick KY-023, dos módulos RGB KY-016 y un receptor infrarrojo KY-022) en un objeto físico con forma de lavadora. Mi trabajo cubrió todo el proceso:

1. **Planificación:** boceto de la carcasa y ubicación de cada componente.
2. **Modelado 3D paramétrico** en OpenSCAD, con todas las medidas como variables.
3. **Validación con plantillas de calce:** piezas pequeñas para probar cada componente antes de imprimir la carcasa completa.
4. **Iteración:** correcciones a partir de mediciones reales y de lo que fallaba en las pruebas.
5. **Impresión final** en una Bambu Lab X1 Carbon.

## 2. Herramientas y tecnologías

| Herramienta | Uso |
|---|---|
| **OpenSCAD** | Modelado 3D paramétrico (todo el diseño es código) |
| **Tinkercad** | Visualización del ensamble por piezas |
| **Bambu Studio** | Laminado y envío de trabajos a la impresora |
| **Bambu Handy** (app móvil) | Monitoreo de las impresiones desde el celular (cámara en vivo, avance y control) |
| **Bambu Lab X1 Carbon** | Impresión 3D (PLA, capa 0.20 mm, 3 paredes, 20 % relleno, sin soportes) |
| **Regla / pie de rey** | Medición de los componentes reales |

### Relación con los paradigmas del curso

OpenSCAD usa un enfoque **declarativo y funcional**: el modelo no se dibuja a mano, se **describe** con funciones y módulos que combinan formas (unión, diferencia, intersección). Las "variables" funcionan como valores inmutables, y las piezas se generan a partir de ellas. Esto permitió que un solo cambio, como el diámetro del agujero de los tornillos, se propagara automáticamente a todas las piezas del diseño.

## 3. Estructura del diseño

La carcasa mide **160 × 240 × 80 mm** (más 18 mm de la sección superior) y está formada por:

| Pieza | Función |
|---|---|
| `cuerpo` | Caja principal; frente con ventanas para LCD, joystick y la puerta; postes internos |
| `modulo_superior` | Sección elevada con dos LEDs RGB y el receptor IR |
| `pancita_ir` | Tapa hueca sobre el conector del IR |
| `tapa_trasera` | Cierre trasero, guía para los 2 protoboards y salida de cables |
| `puerta` + `bisagra` + `pestillo` + pasador | Puerta que abre para ver el interior, con cierre tipo microondas |
| `bandeja_uno` | Bandeja deslizable para el Arduino UNO en la pared derecha |
| `soporte_joystick` | Soporte trasero del joystick |
| `puente` (×3) | Sujetadores de las plaquitas RGB/IR |
| `plantilla_lcd`, `plantilla_joystick`, `plantilla_superior` | Piezas de prueba de calce |

---

## 4. Registro cronológico

### Fase 1 — Planificación (agosto – octubre)

**5 de agosto — Inicio del proyecto.** Al principio el equipo no tenía definido qué proyecto desarrollar ni qué problemática real resolver. Dedicamos las primeras semanas a analizar ideas y opciones que cumplieran con lo pedido: una solución IoT con dispositivos programables que atendiera un problema del entorno.

**Definición de LavaRESI.** Después de ese proceso identificamos una problemática real en las **residencias estudiantiles de la Universidad Nacional**: las lavadoras son compartidas y se generan filas, porque los estudiantes no saben si la **lavadora** o la **secadora** están ocupadas o desocupadas hasta que van a revisar. Decidimos desarrollar **LavaRESI**, un prototipo IoT con ESP32 que simula una lavadora-secadora real y permite conocer el estado de cada una (ocupada o desocupada), para que la siguiente persona sepa cuándo puede pasar a lavar o a secar.

Luego hicimos el reparto de roles. A mí me correspondió el **diseño y la fabricación de la carcasa**.

**Selección de componentes.** Definimos los componentes del prototipo: ESP32, Arduino UNO, pantalla LCD 16x2 con I2C, joystick, dos módulos RGB, un receptor infrarrojo y protoboards.

**Boceto de la carcasa.** Elaboré un boceto con forma de lavadora, con vistas frontal, superior, trasera, interna y lateral, medidas generales de **16 × 24 × 8 cm** y la ubicación de cada componente. Este boceto fue la base del modelado 3D.

---

### 28 de octubre — Inicio del modelado 3D

**Actividades**
- Partí del boceto de la carcasa y de fotos de cada componente real.
- Elegí **OpenSCAD** porque permite cambiar cualquier medida en el código y regenerar todas las piezas.
- Creé el primer modelo paramétrico: cuerpo, sección superior, tapa trasera y puerta.
- Diseñé las **plantillas de calce** para probar el LCD, el joystick y los módulos RGB/IR antes de imprimir la carcasa completa.
- Creé un visor 3D web para revisar el ensamble con cortes, transparencia y vista explosionada.

**Decisiones y ajustes**
- **Protoboards:** el diseño original suponía uno solo. Confirmé que eran **dos de 830 puntos** (63 filas), unidos y compartiendo una tira de alimentación, y ajusté la guía de la tapa trasera a **100 × 165 mm**.
- **Joystick:** medí 12 mm entre la placa y el borde del domo, y un domo de 28 mm de diámetro que se mueve en todas direcciones. Con eso descubrí que unos postes entre la placa y el panel chocarían con el domo. **Solución:** un **soporte trasero** atornillado a columnas ubicadas fuera del radio de giro del domo.
- Registré mis mediciones con regla en un documento: plaquita RGB 14 × 16 mm, plaquita IR 15.5 × 19 mm, receptor IR 6 × 9 mm, posición del LED y alturas bajo el techo.

**Aprendizaje:** medir antes de modelar. Varias medidas que había estimado a partir de fotos estaban mal, sobre todo las del joystick.

---

### 28 de octubre (noche) — Puerta funcional y reubicación del Arduino

**Decisiones**
- Quise que la puerta **abriera de verdad** para ver el interior. Agregué una **bisagra** impresa, una ventana en el frente y un pasador hecho con filamento de 1.75 mm.
- Moví el **Arduino UNO** a una **bandeja deslizable con rieles** en la pared derecha, para que no tapara la vista por la ventana y se pudiera sacar fácilmente.

---

### 29 de octubre — Cierre de la puerta, agarradera y tornillería

**Actividades y decisiones**
- **Cierre:** primero planteé imanes de neodimio. Lo cambié por un **pestillo de gancho flexible tipo microondas**, que no necesita piezas compradas. Luego reduje el gancho (11 × 5 × 1.4 mm) porque se veía demasiado grande.
- **Agarradera:** la primera versión sobresalía. Tomé como referencia una lavadora UniMac de la universidad y la cambié por una **ranura hundida en la cara de la puerta**, integrada al diseño.
- Verifiqué las posiciones estándar de los 4 agujeros del Arduino UNO (R3).
- Preparé las piezas para **Tinkercad**: 10 STL separados que caen alineados al importarlos.
- Armé la **lista de tornillería**: 30 tornillos M3 de 6, 8 y 10 mm, con su tipo de cabeza (redonda, avellanada o baja), y busqué ferreterías en Liberia donde conseguirlos.

**Problema encontrado y corregido**
- Al revisar el largo de cada tornillo contra la profundidad de los postes, encontré que en el **LCD** y en el **soporte del joystick** el tornillo topaba con el fondo antes de apretar. Hice los agujeros más profundos y ajusté la lista de tornillos.

**Aprendizaje:** OpenSCAD es sensible a la sintaxis. Un error de parser vino de escribir `2,5` en vez de `2.5`: los decimales van con punto.

---

### 3 de noviembre — Primeras pruebas de impresión

**Actividades**
- Verifiqué que todas las piezas caben en la **Bambu Lab X1 Carbon** (cama de 256 × 256 × 256 mm). La más grande, el cuerpo, mide 160 × 243 × 80 mm.
- Imprimí y probé las plantillas de calce.

**Resultados de las plantillas y cambios**
- **Agujero para tornillo M3:** de los postes de prueba (2.4 / 2.6 / 2.8 mm), solo el de **2.8 mm** permitió entrar al tornillo. Cambié **todo el diseño a 2.8 mm** e hice una nueva plantilla con postes de 2.8 / 2.9 / 3.0 mm, grabados con su medida.
- **Receptor IR:** el conector de los cables chocaba con el techo y el receptor no asomaba lo suficiente. Medí que el conector sube 4 mm y el receptor 7 mm sobre la placa. Primera solución: un **rebaje de 1.2 mm** por dentro del techo.

---

### 7 de noviembre — Corrección del módulo infrarrojo

**Problema:** en la plantilla, el rebaje no fue suficiente y el conector seguía chocando.

**Solución**
- Abrí completamente el techo sobre el conector y diseñé una **"pancita"**: una tapa hueca que sobresale 5 mm y deja casi 8 mm libres por dentro.
- La hice como **pieza aparte**, porque la sección superior se imprime con el techo sobre la cama y una joroba integrada no se podía imprimir.
- Subí la placa IR para que el receptor asome **3 mm**.
- Con la plantilla elegí el agujero del receptor que mejor calzaba: **7.0 × 10.0 mm**.

**Estimación de la impresión final:** unas **10 – 13 horas** y **≈ 530 g** de PLA en 3 tandas: cuerpo, tapa trasera y piezas pequeñas.

---

### 11 de noviembre — Preparación e inicio de la impresión final

**Actividades**
- Configuré **Bambu Studio**: X1 Carbon con boquilla de 0.4 mm, PLA Basic, placa PEI texturizada, perfil 0.20 mm Standard, 3 paredes, 20 % de relleno y sin soportes.
- Importé las piezas como objetos independientes, las acomodé automáticamente en camas separadas y laminé.
- Imprimí las piezas finales en este orden, una cama a la vez:
  1. **Cuerpo**, la pieza más grande y larga.
  2. **Tapa trasera**.
  3. **Piezas pequeñas** (sección superior, puerta, bandeja del UNO, bisagra, pestillos, soporte del joystick, puentes y pancita), que Bambu Studio estimó en **1 h 48 min y 62 g**.
- Usé la app **Bambu Handy** en el celular para seguir la impresión a distancia: ver la cámara en vivo, el avance y el tiempo restante, y poder pausar o cancelar si algo salía mal.

**Aprendizaje:** el flujo completo de impresión: laminar en la computadora, revisar la vista previa, asignar el filamento del AMS, activar la nivelación automática, vigilar la primera capa y luego monitorear desde el celular, sin tener que estar junto a la impresora durante las horas que dura.

---

###  11 – 14 de noviembre — Impresiones finales y ensamble

> **Pendiente...**

