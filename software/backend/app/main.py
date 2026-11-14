"""LavaRESI - Servidor FastAPI con actualización en tiempo real."""

import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_PATH
from .db import cerrar_pool, inicializar, lectura, obtener_pool, transaccion
from .rutas import publico, terminal, web, eventos
from .servicios import turnos
from .servicios.turnos import ErrorNegocio

log = logging.getLogger("lavaresi")


# --------------------------------------------
# REVISIÓN AUTOMÁTICA DE CICLOS
# --------------------------------------------
# CAMBIO: antes se abría una transacción con el candado global cada
# 1.5 s y todas las demás peticiones tenían que esperar. Ahora se hace
# UNA consulta de lectura (sin candado) y solo se escribe cuando de
# verdad venció un ciclo. Los cambios hechos desde la web o el ESP32
# ya avisan por WebSocket en sus propias rutas.

def comprobar_cambios() -> bool:
    """Devuelve True si algún ciclo venció y se actualizó la base."""

    with lectura() as conn:
        activos = conn.execute("""
            SELECT fecha_inicio, duracion_minutos
            FROM ciclos
            WHERE estado = 'EN_CURSO'
        """).fetchall()

    ahora = datetime.now(timezone.utc)

    hay_vencido = any(
        turnos._fecha(c["fecha_inicio"])
        + timedelta(minutes=c["duracion_minutos"]) <= ahora
        for c in activos
    )

    if not hay_vencido:
        return False

    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)

    return True


async def vigilar_ciclos():
    """Revisa ciclos vencidos sin bloquear la atención de FastAPI."""

    while True:
        try:
            if await asyncio.to_thread(comprobar_cambios):
                await eventos.avisar_cambio()

        except asyncio.CancelledError:
            raise

        except Exception:
            log.exception("Error al revisar los ciclos de LavaRESI")

        await asyncio.sleep(1.5)


# --------------------------------------------
# INICIO Y CIERRE DEL SERVIDOR
# --------------------------------------------

@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):

    inicializar()

    # Abre las conexiones a Neon desde el arranque (no en la 1.ª petición).
    await asyncio.to_thread(obtener_pool)

    tarea = asyncio.create_task(vigilar_ciclos())

    try:
        yield

    finally:
        tarea.cancel()

        with suppress(asyncio.CancelledError):
            await tarea

        cerrar_pool()


# --------------------------------------------
# APLICACIÓN FASTAPI
# --------------------------------------------

app = FastAPI(
    title="LavaRESI",
    lifespan=ciclo_de_vida
)


@app.exception_handler(ErrorNegocio)
async def manejar_error_negocio(
    request: Request,
    exc: ErrorNegocio
):
    return JSONResponse(
        status_code=exc.codigo,
        content={"detail": exc.mensaje}
    )


# Rutas de la API
app.include_router(publico.router)
app.include_router(terminal.router)
app.include_router(web.router)

# WebSocket para notificaciones en tiempo real
app.include_router(eventos.router)

# Archivos de la página web
app.mount(
    "/",
    StaticFiles(
        directory=FRONTEND_PATH,
        html=True
    ),
    name="frontend"
)