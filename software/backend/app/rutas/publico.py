from fastapi import APIRouter

from ..db import transaccion
from ..servicios import turnos

router = APIRouter(prefix="/api")


@router.get("/health")
def verificar_conexion():
    """El ESP32 ya consulta esta ruta para probar la conexión."""
    return {"estado": "ok", "mensaje": "LavaRESI conectado"}


@router.get("/estado")
def estado():
    """Estado de las dos máquinas y sus colas (lo usan la web y la terminal)."""
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        return turnos.estado_general(conn)
