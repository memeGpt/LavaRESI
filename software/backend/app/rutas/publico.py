"""
LavaRESI - Rutas públicas.

Sin iniciar sesión:
    Se puede ver la disponibilidad de las máquinas,
    el tiempo restante y cuántas personas esperan.

Con sesión iniciada:
    Se pueden ver los nombres y las colas completas.

ESP32 autorizado:
    Puede consultar la información completa utilizando
    su clave X-Terminal-Key.
"""

import hmac

from fastapi import (
    APIRouter,
    Cookie,
    Header,
    HTTPException
)

from ..config import TERMINAL_KEY
from ..db import lectura
from ..seguridad import leer_token
from ..servicios import turnos


router = APIRouter(prefix="/api")


# ==========================================
# COMPROBAR CONEXIÓN DEL SERVIDOR
# ==========================================

@router.get("/health")
def verificar_conexion():
    return {
        "estado": "ok",
        "mensaje": "LavaRESI conectado"
    }


# ==========================================
# ESTADO DE LAVADORA Y SECADORA
# ==========================================

@router.get("/estado")
def estado(
    lavaresi_sesion: str | None = Cookie(default=None),
    x_terminal_key: str | None = Header(default=None)
):

    # Verificar si la solicitud viene del ESP32
    # utilizando la clave de terminal configurada.

    terminal_autorizada = bool(
        TERMINAL_KEY
        and x_terminal_key
        and hmac.compare_digest(
            TERMINAL_KEY,
            x_terminal_key
        )
    )

    # Si se proporciona una clave incorrecta,
    # rechazar la solicitud.
    if (
        x_terminal_key is not None
        and not terminal_autorizada
    ):
        raise HTTPException(
            status_code=401,
            detail="Terminal no autorizada"
        )

    # Verificar la cookie de sesión de la web.
    usuario_id = leer_token(lavaresi_sesion)

    with lectura() as conn:

        # (Los ciclos vencidos los actualiza main.vigilar_ciclos.)

        sesion_valida = False

        if usuario_id is not None:
            usuario = conn.execute(
                """
                SELECT 1
                FROM usuarios
                WHERE id = %s
                  AND activo = 1
                """,
                (usuario_id,)
            ).fetchone()

            sesion_valida = usuario is not None

        # Consultar el estado completo de las máquinas.
        datos = turnos.estado_general(conn)

    # ======================================
    # ACCESO PRIVADO
    # ======================================

    # Las cuentas autenticadas y el ESP32
    # pueden consultar las colas completas.

    if sesion_valida or terminal_autorizada:
        return datos

    # ======================================
    # ACCESO PÚBLICO
    # ======================================

    # Los visitantes no reciben nombres,
    # identificadores de solicitudes ni
    # información personal de los estudiantes.

    maquinas_publicas = []

    for maquina in datos["maquinas"]:

        personas_esperando = sum(
            1
            for solicitud in maquina["cola"]
            if solicitud["estado"] != "EN_USO"
        )

        maquinas_publicas.append({
            "id": maquina["id"],
            "tipo": maquina["tipo"],
            "estado": maquina["estado"],
            "segundos_restantes":
                maquina["segundos_restantes"],
            "personas_en_espera":
                personas_esperando
        })

    return {
        "maquinas": maquinas_publicas
    }