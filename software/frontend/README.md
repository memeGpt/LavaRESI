# LavaRESI · Frontend

Página web en HTML, CSS y JavaScript puro (sin build ni dependencias). La sirve el backend en `/`,
por lo que no hay que levantar nada aparte: ver `../backend/README.md`.

- **Estado**: las dos máquinas con su estado, quién las usa, cuenta regresiva y la cola (se actualiza cada 5 s).
- **Mi cuenta**: registro/ingreso, pedir turno, marcarse ausente/disponible, cancelar y ver avisos.

Archivos: `index.html`, `css/estilos.css`, `js/app.js`. Los textos de los usuarios se insertan con `textContent`
(no `innerHTML`) para evitar inyección de HTML.
