"""Puente con SWI-Prolog. Envía un JSON por stdin y lee la decisión por stdout.
Si 'swipl' no está instalado, usa un respaldo en Python con las mismas reglas
para que el sistema siga funcionando (se avisa por log)."""
import json
import logging
import shutil
import subprocess

from ..config import PROLOG_PATH

log = logging.getLogger("lavaresi.prolog")


def consultar(entrada: dict) -> dict:
    if shutil.which("swipl"):
        try:
            p = subprocess.run(
                ["swipl", "-q", "-s", str(PROLOG_PATH), "-g", "main", "-t", "halt"],
                input=json.dumps(entrada), capture_output=True, text=True, timeout=10,
            )
            return json.loads(p.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
            log.warning("Fallo SWI-Prolog (%s); se usa el respaldo en Python", e)
    else:
        log.warning("swipl no encontrado; se usa el respaldo en Python")
    return _respaldo(entrada)


def _respaldo(d: dict) -> dict:
    """Misma lógica que reglas_turnos.pl, solo como plan B."""
    m, est = d["maquina_id"], d["estado_maquina"]
    sol = sorted((s for s in d["solicitudes"] if s["maquina_id"] == m), key=lambda s: s["id"])
    ocupante = next((s for s in sol if s["estado"] == "EN_USO"), None)

    def siguiente():
        if est != "LIBRE":
            if ocupante:
                return {"accion": "MANTENER", "solicitud_id": ocupante["id"], "motivo": "MAQUINA_OCUPADA"}
            return {"accion": "ESPERAR", "motivo": "MAQUINA_OCUPADA_SIN_TURNO_VALIDO"}
        if ocupante:
            return {"accion": "ESPERAR", "motivo": "ESTADO_INCONSISTENTE_OCUPANTE"}
        reserva = next((s for s in sol if s["estado"] == "AUTORIZADA"), None)
        if reserva:
            if reserva["disponible"] == 1:
                return {"accion": "AUTORIZAR", "solicitud_id": reserva["id"], "motivo": "RESERVA_EXISTENTE"}
            return {"accion": "ESPERAR", "motivo": "REVISAR_RESERVA_NO_DISPONIBLE"}
        elegible = next((s for s in sol if s["estado"] == "EN_ESPERA" and s["disponible"] == 1
                         and s["tandas_iniciadas"] == 0), None)
        if elegible:
            return {"accion": "AUTORIZAR", "solicitud_id": elegible["id"], "motivo": "PRIMER_DISPONIBLE"}
        return {"accion": "ESPERAR", "motivo": "SIN_SOLICITUDES_DISPONIBLES"}

    accion = d.get("accion")
    if accion == "SIGUIENTE":
        return siguiente()
    s = next((x for x in sol if x["id"] == d.get("solicitud_id")), None)
    if accion == "INICIAR" and s:
        n = d.get("numero_tanda")
        if n == s["tandas_iniciadas"] + 1 and n <= s["tandas_totales"]:
            sig = siguiente()
            if (est == "LIBRE" and n == 1 and sig.get("accion") == "AUTORIZAR"
                    and sig["solicitud_id"] == s["id"]) or \
               (est == "ENTRE_TANDAS" and s["estado"] == "EN_USO"):
                return {"permitido": True, "motivo": "INICIO_AUTORIZADO"}
        return {"permitido": False, "motivo": "NO_ES_SU_TURNO_O_TANDA_INVALIDA"}
    if accion == "RETIRAR":
        if est == "PENDIENTE_RETIRO" and s and s["estado"] == "EN_USO" and s["tandas_iniciadas"] > 0:
            if s["tandas_iniciadas"] < s["tandas_totales"]:
                return {"permitido": True, "resultado": "CONTINUAR_TANDAS", "motivo": "CONSERVA_TURNO"}
            return {"permitido": True, "resultado": "LIBERAR_MAQUINA", "motivo": "ULTIMA_TANDA_RETIRADA"}
        return {"permitido": False, "motivo": "RETIRO_NO_AUTORIZADO"}
    return {"accion": "ERROR", "motivo": "ENTRADA_INVALIDA"}
