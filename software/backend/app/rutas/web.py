"""
LavaRESI - Rutas de estudiantes.

- Registro e inicio de sesión.
- Sesiones protegidas mediante cookies.
- Solicitud y cancelación de turnos.
- Cambios de disponibilidad.
- Notificaciones del estudiante.
- Avisos WebSocket cuando cambian los turnos.
"""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    HTTPException,
    Request,
    Response,
)

from ..db import lectura, transaccion
from ..modelos.esquemas import (
    DisponibilidadIn,
    LoginIn,
    RegistroIn,
    SolicitudWebIn,
)
from ..seguridad import crear_token, leer_token, limite
from ..servicios import turnos
from .eventos import avisar_cambio


router = APIRouter(prefix="/api")

COOKIE = "lavaresi_sesion"


# ==========================================
# SESIONES
# ==========================================

def poner_cookie(resp: Response, usuario_id: int):
    resp.set_cookie(
        key=COOKIE,
        value=crear_token(usuario_id),
        httponly=True,
        samesite="lax",
        max_age=12 * 3600,
        path="/",
    )


def exigir_sesion(conn, token):
    """Verifica que la sesión exista y la cuenta esté activa."""

    usuario_id = leer_token(token)

    if usuario_id is None:
        raise HTTPException(
            status_code=401,
            detail="Inicia sesión para continuar",
        )

    usuario = conn.execute(
        """
        SELECT id
        FROM usuarios
        WHERE id = %s AND activo = 1
        """,
        (usuario_id,),
    ).fetchone()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Sesión inválida o cuenta inactiva",
        )

    return usuario_id


# ==========================================
# CREAR CUENTA
# ==========================================

@router.post("/auth/registro")
def registro(datos: RegistroIn, resp: Response):

    with transaccion() as conn:
        usuario_id = turnos.registrar_usuario(
            conn,
            datos.nombre,
            datos.usuario,
            datos.pin,
            datos.password,
        )

        resultado = turnos.datos_usuario(
            conn,
            usuario_id,
        )

    # La cuenta queda iniciada tras registrarse.
    poner_cookie(resp, usuario_id)

    return resultado


# ==========================================
# INICIAR SESIÓN
# ==========================================

@router.post("/auth/login")
def login(
    datos: LoginIn,
    resp: Response,
    request: Request,
):

    ip = request.client.host if request.client else "?"

    if limite.bloqueado(ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos. Espera un minuto.",
        )

    with transaccion() as conn:

        try:
            usuario_id = turnos.login(
                conn,
                datos.usuario,
                datos.password,
            )

        except turnos.ErrorNegocio:
            limite.registrar_fallo(ip)
            raise

        resultado = turnos.datos_usuario(
            conn,
            usuario_id,
        )

    poner_cookie(resp, usuario_id)

    return resultado


# ==========================================
# CERRAR SESIÓN
# ==========================================

@router.post("/auth/logout")
def logout(resp: Response):

    resp.delete_cookie(
        key=COOKIE,
        path="/",
    )

    return {"ok": True}


# ==========================================
# CONSULTAR MI CUENTA
# ==========================================

@router.get("/yo")
def yo(
    lavaresi_sesion: str | None = Cookie(default=None),
):

    with lectura() as conn:

        usuario_id = exigir_sesion(
            conn,
            lavaresi_sesion,
        )

        usuario = turnos.datos_usuario(
            conn,
            usuario_id,
        )

        solicitudes = turnos.solicitudes_de(
            conn,
            usuario_id,
        )

        avisos = turnos.notificaciones(
            conn,
            usuario_id,
        )

    return {
        "usuario": usuario,
        "solicitudes": solicitudes,
        "notificaciones": avisos,
        "no_leidas": sum(
            not aviso["leida"]
            for aviso in avisos
        ),
    }


# ==========================================
# SOLICITAR TURNO
# ==========================================

@router.post("/solicitudes")
def pedir_turno(
    datos: SolicitudWebIn,
    tareas: BackgroundTasks,
    lavaresi_sesion: str | None = Cookie(default=None),
):

    with transaccion() as conn:

        usuario_id = exigir_sesion(
            conn,
            lavaresi_sesion,
        )

        turnos.actualizar_ciclos(conn)

        resultado = turnos.crear_solicitud(
            conn,
            usuario_id,
            datos.maquina_id,
            datos.tandas,
        )

    # Avisar después de guardar los cambios.
    tareas.add_task(avisar_cambio)

    return resultado


# ==========================================
# CANCELAR SOLICITUD
# ==========================================

@router.post("/solicitudes/{sid}/cancelar")
def cancelar(
    sid: int,
    tareas: BackgroundTasks,
    lavaresi_sesion: str | None = Cookie(default=None),
):

    with transaccion() as conn:

        usuario_id = exigir_sesion(
            conn,
            lavaresi_sesion,
        )

        turnos.actualizar_ciclos(conn)

        turnos.cancelar(
            conn,
            usuario_id,
            sid,
        )

    tareas.add_task(avisar_cambio)

    return {"ok": True}


# ==========================================
# CAMBIAR DISPONIBILIDAD
# ==========================================

@router.post("/solicitudes/{sid}/disponibilidad")
def cambiar_disponibilidad(
    sid: int,
    datos: DisponibilidadIn,
    tareas: BackgroundTasks,
    lavaresi_sesion: str | None = Cookie(default=None),
):

    with transaccion() as conn:

        usuario_id = exigir_sesion(
            conn,
            lavaresi_sesion,
        )

        turnos.actualizar_ciclos(conn)

        turnos.cambiar_disponibilidad(
            conn,
            usuario_id,
            sid,
            datos.disponible,
        )

    # Actualizar las listas de los navegadores.
    tareas.add_task(avisar_cambio)

    return {
        "ok": True,
        "disponible": datos.disponible,
    }


# ==========================================
# MARCAR NOTIFICACIONES COMO LEÍDAS
# ==========================================

@router.post("/notificaciones/leidas")
def marcar_leidas(
    lavaresi_sesion: str | None = Cookie(default=None),
):

    with transaccion() as conn:

        usuario_id = exigir_sesion(
            conn,
            lavaresi_sesion,
        )

        conn.execute(
            """
            UPDATE notificaciones
            SET leida = 1
            WHERE usuario_id = %s
            """,
            (usuario_id,),
        )

    return {"ok": True}