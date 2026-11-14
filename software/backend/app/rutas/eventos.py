
"""LavaRESI - Notificaciones WebSocket."""

import asyncio
import logging

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

router = APIRouter()

log = logging.getLogger("lavaresi.eventos")

# Navegadores conectados
conectados: set[WebSocket] = set()


@router.websocket("/ws/estado")
async def recibir_eventos(ws: WebSocket):

    await ws.accept()

    conectados.add(ws)

    try:
        await ws.send_json({
            "tipo": "conectado"
        })

        while True:
            await ws.receive_text()

    except WebSocketDisconnect:
        pass

    except Exception:
        log.exception(
            "Error de comunicación WebSocket"
        )

    finally:
        conectados.discard(ws)


async def avisar_cambio():
    """Informa que hay datos nuevos disponibles."""

    for ws in tuple(conectados):

        try:
            await asyncio.wait_for(
                ws.send_json({
                    "tipo": "actualizar"
                }),
                timeout=2.0
            )

        except Exception:
            conectados.discard(ws)
