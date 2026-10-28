# LavaRESI · Backend

API en **FastAPI** + base de datos **SQLite** + reglas de turnos en **SWI-Prolog**.
El mismo servidor entrega la página web (`software/frontend`), así que solo hay que levantar una cosa.

## Cómo ejecutarlo

```bash
cd software/backend
pip install -r requirements.txt
python database/inicializar_db.py --demo     # crea lavaresi.db (+ usuarios de prueba)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Página web: http://localhost:8000
- Documentación automática de la API: http://localhost:8000/docs
- `--host 0.0.0.0` es necesario para que el ESP32 pueda conectarse desde la red WiFi.
  Si usas Windows, permite el puerto 8000 en el firewall.
- Instala **SWI-Prolog** (`swipl` en el PATH) para usar `prolog/reglas_turnos.pl`.
  Si no está instalado, el backend usa un respaldo en Python con las mismas reglas y lo avisa en el log.

Usuarios demo (`--demo`), con los mismos PIN del código de prueba del ESP32:
Melissa `1234`, Kelvin `2345`, Andy `3456`, Andrei `4567`. Contraseña web: `lavaresi123`.

Variables de entorno opcionales: `LAVARESI_DB` (ruta de la base), `LAVARESI_SECRET` (firma de sesiones),
`LAVARESI_TERMINAL_KEY` (si se define, el ESP32 debe enviarla en el header `X-Terminal-Key`).

## Estructura

```
backend/
├── app/
│   ├── main.py            # arranque, rutas y página web
│   ├── config.py, db.py, seguridad.py
│   ├── modelos/esquemas.py    # validación de datos de entrada
│   ├── rutas/             # publico.py · terminal.py (ESP32) · web.py (navegador)
│   └── servicios/         # turnos.py (lógica) · prolog.py (puente con SWI-Prolog)
├── database/              # schema.sql + inicializar_db.py
└── prolog/reglas_turnos.pl
```

## Cómo se reparten el trabajo

- **SQLite** guarda usuarios, solicitudes, ciclos y avisos.
- **Prolog** decide quién sigue (`SIGUIENTE`), si una tanda puede empezar (`INICIAR`) y si se libera la máquina (`RETIRAR`).
- **Python** valida PIN/sesión, guarda en la base y aplica lo que Prolog decide.
- Los ciclos terminados se detectan al consultar (no hay hilos en segundo plano): cuando pasa el tiempo, la máquina
  pasa a `PENDIENTE_RETIRO` y se avisa al estudiante.

## API para el ESP32 (`/api/terminal`, el estudiante se identifica con su PIN)

| Método y ruta | Cuerpo JSON | Qué hace |
|---|---|---|
| `GET /api/health` | – | Prueba de conexión |
| `GET /api/estado` | – | Estado de las 2 máquinas, ocupante, segundos restantes y colas |
| `POST /api/terminal/solicitudes` | `{pin, maquina_id, tandas}` | Registrar turno (1 a 3 tandas) |
| `POST /api/terminal/ciclos/iniciar` | `{pin, maquina_id, minutos}` | Iniciar una tanda (1 a 180 min) |
| `POST /api/terminal/ciclos/retirar` | `{pin, maquina_id}` | Confirmar retiro de la ropa |
| `POST /api/terminal/mi-turno` | `{pin}` | Solicitudes activas del estudiante |

`maquina_id`: `1` = lavadora, `2` = secadora. Errores: `401` PIN incorrecto, `409` no es su turno / ya existe,
`429` demasiados PIN fallidos (máx. 10 por minuto por IP).

## API de la web (`/api`, sesión por cookie)

`POST /auth/registro`, `POST /auth/login`, `POST /auth/logout`, `GET /yo`, `POST /solicitudes`,
`POST /solicitudes/{id}/cancelar`, `POST /solicitudes/{id}/disponibilidad`, `POST /notificaciones/leidas`.

## Notas

- `app/prueba_conexion.py` quedó del primer prototipo; ya no se usa (`/api/health` está en `rutas/publico.py`).
- Los PIN y contraseñas se guardan con hash PBKDF2, nunca en texto plano. El PIN debe ser único entre usuarios.
