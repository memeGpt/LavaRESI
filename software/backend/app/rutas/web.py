"""Endpoints para la página web (sesión por cookie)."""
from fastapi import APIRouter, Cookie, HTTPException, Request, Response

from ..db import transaccion
from ..modelos.esquemas import DisponibilidadIn, LoginIn, RegistroIn, SolicitudWebIn
from ..seguridad import crear_token, leer_token, limite
from ..servicios import turnos

router = APIRouter(prefix="/api")
COOKIE = "lavaresi_sesion"


def _poner_cookie(resp: Response, usuario_id: int):
    resp.set_cookie(COOKIE, crear_token(usuario_id), httponly=True, samesite="lax", max_age=12 * 3600)


def _sesion(token) -> int:
    uid = leer_token(token)
    if uid is None:
        raise HTTPException(401, "Inicia sesión para continuar")
    return uid


@router.post("/auth/registro")
def registro(datos: RegistroIn, resp: Response):
    with transaccion() as conn:
        uid = turnos.registrar_usuario(conn, datos.nombre, datos.usuario, datos.pin, datos.password)
        _poner_cookie(resp, uid)
        return turnos.datos_usuario(conn, uid)


@router.post("/auth/login")
def login(datos: LoginIn, resp: Response, request: Request):
    ip = request.client.host if request.client else "?"
    if limite.bloqueado(ip):
        raise HTTPException(429, "Demasiados intentos. Espera un minuto.")
    with transaccion() as conn:
        try:
            uid = turnos.login(conn, datos.usuario, datos.password)
        except turnos.ErrorNegocio:
            limite.registrar_fallo(ip)
            raise
        _poner_cookie(resp, uid)
        return turnos.datos_usuario(conn, uid)


@router.post("/auth/logout")
def logout(resp: Response):
    resp.delete_cookie(COOKIE)
    return {"ok": True}


@router.get("/yo")
def yo(lavaresi_sesion: str | None = Cookie(default=None)):
    uid = _sesion(lavaresi_sesion)
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        usuario = turnos.datos_usuario(conn, uid)
        if not usuario:
            raise HTTPException(401, "Sesión inválida")
        notis = turnos.notificaciones(conn, uid)
        return {"usuario": usuario, "solicitudes": turnos.solicitudes_de(conn, uid),
                "notificaciones": notis, "no_leidas": sum(not n["leida"] for n in notis)}


@router.post("/solicitudes")
def pedir_turno(datos: SolicitudWebIn, lavaresi_sesion: str | None = Cookie(default=None)):
    uid = _sesion(lavaresi_sesion)
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        return turnos.crear_solicitud(conn, uid, datos.maquina_id, datos.tandas)


@router.post("/solicitudes/{sid}/cancelar")
def cancelar(sid: int, lavaresi_sesion: str | None = Cookie(default=None)):
    uid = _sesion(lavaresi_sesion)
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        turnos.cancelar(conn, uid, sid)
        return {"ok": True}


@router.post("/solicitudes/{sid}/disponibilidad")
def disponibilidad(sid: int, datos: DisponibilidadIn, lavaresi_sesion: str | None = Cookie(default=None)):
    uid = _sesion(lavaresi_sesion)
    with transaccion() as conn:
        turnos.actualizar_ciclos(conn)
        turnos.cambiar_disponibilidad(conn, uid, sid, datos.disponible)
        return {"ok": True}


@router.post("/notificaciones/leidas")
def marcar_leidas(lavaresi_sesion: str | None = Cookie(default=None)):
    uid = _sesion(lavaresi_sesion)
    with transaccion() as conn:
        conn.execute("UPDATE notificaciones SET leida = 1 WHERE usuario_id = ?", (uid,))
        return {"ok": True}
