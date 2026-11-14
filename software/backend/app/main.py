
"""LavaRESI - Servidor FastAPI con actualización en tiempo real."""

import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_PATH
from .db import inicializar, transaccion
from .rutas import publico, terminal, web, eventos
from .servicios import turnos
from .servicios.turnos import ErrorNegocio

log = logging.getLogger("lavaresi")


# --------------------------------------------
# REVISIÓN AUTOMÁTICA DE CICLOS
# --------------------------------------------

def comprobar_cambios():
    """Consulta ciclos vencidos y detecta cambios de estado."""

    with transaccion() as conn:

        # Marca como terminados los ciclos cuyo tiempo finalizó.
        turnos.actualizar_ciclos(conn)

        maquinas = conn.execute("""
            SELECT id, estado
            FROM maquinas
            ORDER BY id
        """).fetchall()

        solicitudes = conn.execute("""
            SELECT id, estado, disponible, tandas_iniciadas
            FROM solicitudes
            WHERE estado IN (
                'EN_ESPERA',
                'AUTORIZADA',
                'EN_USO'
            )
            ORDER BY id
        """).fetchall()

        estado_actual = (
            tuple(
                (m["id"], m["estado"])
                for m in maquinas
            ),
            tuple(
                (
                    s["id"],
                    s["estado"],
                    s["disponible"],
                    s["tandas_iniciadas"]
                )
                for s in solicitudes
            )
        )

        return estado_actual


async def vigilar_ciclos():
    """Revisa cambios sin bloquear la atención de FastAPI."""

    estado_anterior = None

    while True:
        try:
            estado_actual = await asyncio.to_thread(
                comprobar_cambios
            )

            if (
                estado_anterior is not None
                and estado_actual != estado_anterior
            ):
                await eventos.avisar_cambio()

            estado_anterior = estado_actual

        except asyncio.CancelledError:
            raise

        except Exception:
            log.exception(
                "Error al revisar los ciclos de LavaRESI"
            )

        await asyncio.sleep(1.5)


# --------------------------------------------
# INICIO Y CIERRE DEL SERVIDOR
# --------------------------------------------

@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):

    inicializar()

    tarea = asyncio.create_task(vigilar_ciclos())

    try:
        yield

    finally:
        tarea.cancel()

        with suppress(asyncio.CancelledError):
            await tarea


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
