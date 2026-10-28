"""Endpoints para el ESP32. El estudiante se identifica con su PIN."""
from fastapi import APIRouter, Depends, Header, HTTPException, Request

from ..config import TERMINAL_KEY
from ..db import transaccion
from ..modelos.esquemas import IniciarIn, MiTurnoIn, RetirarIn, SolicitudTerminalIn
from ..seguridad import limite
from ..servicios import turnos


def verificar_terminal(x_terminal_key: str = Header(default="")):
    if TERMINAL_KEY and x_terminal_key != TERMINAL_KEY:
        raise HTTPException(401, "Terminal no autorizada")


router = APIRouter(prefix="/api/terminal", dependencies=[Depends(verificar_terminal)])


def _usuario(conn, pin, request: Request):
    ip = request.client.host if request.client else "?"
    if limite.bloqueado(ip):
        raise turnos.ErrorNegocio("Demasiados PIN incorrectos. Espera un minuto.", 429)
    try:
        return turnos.usuario_por_pin(conn, pin)
    except turnos.ErrorNegocio:
        limite.registrar_fallo(ip)
        raise


@router.post("/solicitudes")
def pedir_turno(datos: SolicitudTerminalIn, request: Request):
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        u = _usuario(conn, datos.pin, request)
        return turnos.crear_solicitud(conn, u["id"], datos.maquina_id, datos.tandas) | {"nombre": u["nombre"]}


@router.post("/ciclos/iniciar")
def iniciar(datos: IniciarIn, request: Request):
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        u = _usuario(conn, datos.pin, request)
        return turnos.iniciar_ciclo(conn, u["id"], datos.maquina_id, datos.minutos) | {"nombre": u["nombre"]}


@router.post("/ciclos/retirar")
def retirar(datos: RetirarIn, request: Request):
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        u = _usuario(conn, datos.pin, request)
        return turnos.retirar(conn, u["id"], datos.maquina_id) | {"nombre": u["nombre"]}


@router.post("/mi-turno")
def mi_turno(datos: MiTurnoIn, request: Request):
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        u = _usuario(conn, datos.pin, request)
        return {"nombre": u["nombre"], "solicitudes": turnos.solicitudes_de(conn, u["id"])}
