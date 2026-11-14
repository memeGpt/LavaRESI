
"""
LavaRESI - API de la terminal ESP32.

Funciones:
- Validar la clave de la terminal.
- Identificar estudiantes mediante PIN.
- Registrar solicitudes.
- Iniciar ciclos de lavado y secado.
- Confirmar retiros.
- Consultar el turno de un estudiante.
- Avisar a la web cuando cambie un turno.

FastAPI y Prolog siguen controlando las reglas.
"""

import hmac

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Request,
)

from ..config import TERMINAL_KEY
from ..db import transaccion

from ..modelos.esquemas import (
    IniciarIn,
    MiTurnoIn,
    RetirarIn,
    SolicitudTerminalIn,
)

from ..seguridad import limite
from ..servicios import turnos
from .eventos import avisar_cambio


# ==========================================
# AUTORIZACIÓN DEL ESP32
# ==========================================

def verificar_terminal(
    x_terminal_key: str = Header(default="")
):
    """
    Solo permite utilizar estos endpoints
    a una terminal con la clave correcta.
    """

    if not TERMINAL_KEY:
        raise HTTPException(
            status_code=503,
            detail="Clave de terminal no configurada",
        )

    if not hmac.compare_digest(
        x_terminal_key,
        TERMINAL_KEY,
    ):
        raise HTTPException(
            status_code=401,
            detail="Terminal no autorizada",
        )


router = APIRouter(
    prefix="/api/terminal",
    dependencies=[Depends(verificar_terminal)],
)


# ==========================================
# IDENTIFICAR USUARIO POR PIN
# ==========================================

def _usuario(conn, pin: str, request: Request):
    """
    Busca el PIN en PostgreSQL y limita
    los intentos incorrectos.
    """

    ip = (
        request.client.host
        if request.client
        else "?"
    )

    if limite.bloqueado(ip):
        raise turnos.ErrorNegocio(
            "Demasiados PIN incorrectos. Espera un minuto.",
            429,
        )

    try:
        return turnos.usuario_por_pin(
            conn,
            pin,
        )

    except turnos.ErrorNegocio:
        limite.registrar_fallo(ip)
        raise


# ==========================================
# CONSULTAR MI TURNO
# ==========================================

@router.post("/mi-turno")
def mi_turno(
    datos: MiTurnoIn,
    request: Request,
):
    """
    El estudiante ingresa su PIN.
    Devuelve sus solicitudes actuales.
    """

    with transaccion() as conn:

        turnos.actualizar_ciclos(conn)

        usuario = _usuario(
            conn,
            datos.pin,
            request,
        )

        solicitudes = turnos.solicitudes_de(
            conn,
            usuario["id"],
        )

        resultado = {
            "nombre": usuario["nombre"],
            "solicitudes": solicitudes,
        }

    return resultado


# ==========================================
# REGISTRAR SOLICITUD DESDE EL ESP32
# ==========================================

@router.post("/solicitudes")
def pedir_turno(
    datos: SolicitudTerminalIn,
    request: Request,
    tareas: BackgroundTasks,
):
    """
    Registra una solicitud de 1 a 3 tandas.
    Prolog determina la prioridad.
    """

    with transaccion() as conn:

        turnos.actualizar_ciclos(conn)

        usuario = _usuario(
            conn,
            datos.pin,
            request,
        )

        resultado = turnos.crear_solicitud(
            conn,
            usuario["id"],
            datos.maquina_id,
            datos.tandas,
        )

        resultado = {
            **resultado,
            "nombre": usuario["nombre"],
        }

    # Se avisa después de guardar en PostgreSQL.
    tareas.add_task(avisar_cambio)

    return resultado


# ==========================================
# INICIAR CICLO
# ==========================================

@router.post("/ciclos/iniciar")
def iniciar(
    datos: IniciarIn,
    request: Request,
    tareas: BackgroundTasks,
):
    """
    Verifica el PIN y solicita iniciar
    una tanda de lavado o secado.

    Si no corresponde el turno,
    el backend rechaza la operación.
    """

    with transaccion() as conn:

        turnos.actualizar_ciclos(conn)

        usuario = _usuario(
            conn,
            datos.pin,
            request,
        )

        resultado = turnos.iniciar_ciclo(
            conn,
            usuario["id"],
            datos.maquina_id,
            datos.minutos,
        )

        resultado = {
            **resultado,
            "nombre": usuario["nombre"],
        }

    # La página recibe aviso del inicio.
    tareas.add_task(avisar_cambio)

    return resultado


# ==========================================
# CONFIRMAR RETIRO DE ROPA
# ==========================================

@router.post("/ciclos/retirar")
def retirar(
    datos: RetirarIn,
    request: Request,
    tareas: BackgroundTasks,
):
    """
    Confirma el retiro de una tanda terminada.

    Si quedan tandas:
        El estudiante conserva la máquina.

    Si era la última:
        Se libera la máquina y se revisa
        quién sigue en la cola.
    """

    with transaccion() as conn:

        turnos.actualizar_ciclos(conn)

        usuario = _usuario(
            conn,
            datos.pin,
            request,
        )

        resultado = turnos.retirar(
            conn,
            usuario["id"],
            datos.maquina_id,
        )

        resultado = {
            **resultado,
            "nombre": usuario["nombre"],
        }

    # Avisar que hubo un retiro o liberación.
    tareas.add_task(avisar_cambio)

    return resultado
