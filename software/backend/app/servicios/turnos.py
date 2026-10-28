"""Lógica de negocio: usuarios, solicitudes, ciclos y colas.
PostgreSQL guarda los datos; SWI-Prolog decide a quién le toca (ver prolog.py)."""
from datetime import datetime, timedelta, timezone

from ..seguridad import ITER_PASSWORD, ITER_PIN, hashear, verificar
from . import prolog

ACTIVAS = "('EN_ESPERA','AUTORIZADA','EN_USO')"
NOMBRES = {1: "lavadora", 2: "secadora"}


class ErrorNegocio(Exception):
    def __init__(self, mensaje: str, codigo: int = 400):
        super().__init__(mensaje)
        self.mensaje, self.codigo = mensaje, codigo


def _ahora():
    return datetime.now(timezone.utc)


def _fecha(valor) -> datetime:
    if isinstance(valor, datetime):
        return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor.astimezone(timezone.utc)
    return datetime.strptime(str(valor), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def _texto(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def notificar(conn, usuario_id, solicitud_id, mensaje):
    conn.execute("INSERT INTO notificaciones (usuario_id, solicitud_id, mensaje) VALUES (%s,%s,%s)",
                 (usuario_id, solicitud_id, mensaje))


# ------------------------------------------------------------------ usuarios
def registrar_usuario(conn, nombre, usuario, pin, password):
    usuario = usuario.strip().lower()
    if conn.execute("SELECT 1 FROM usuarios WHERE usuario = %s", (usuario,)).fetchone():
        raise ErrorNegocio("Ese nombre de usuario ya existe", 409)
    for u in conn.execute("SELECT pin_hash FROM usuarios"):
        if verificar(pin, u["pin_hash"]):
            raise ErrorNegocio("Ese PIN ya está en uso, elige otro", 409)
    cur = conn.execute(
        "INSERT INTO usuarios (nombre, usuario, pin_hash, password_hash) VALUES (%s,%s,%s,%s) RETURNING id",
        (nombre.strip(), usuario, hashear(pin, ITER_PIN), hashear(password, ITER_PASSWORD)))
    return cur.fetchone()["id"]


def login(conn, usuario, password):
    u = conn.execute("SELECT * FROM usuarios WHERE usuario = %s AND activo = 1",
                     (usuario.strip().lower(),)).fetchone()
    if not u or not verificar(password, u["password_hash"]):
        raise ErrorNegocio("Usuario o contraseña incorrectos", 401)
    return u["id"]


def usuario_por_pin(conn, pin):
    for u in conn.execute("SELECT * FROM usuarios WHERE activo = 1"):
        if verificar(pin, u["pin_hash"]):
            return u
    raise ErrorNegocio("PIN incorrecto", 401)


def datos_usuario(conn, usuario_id):
    u = conn.execute("SELECT id, nombre, usuario FROM usuarios WHERE id = %s", (usuario_id,)).fetchone()
    return dict(u) if u else None


# ------------------------------------------------------------------ Prolog
def _consultar(conn, accion, maquina_id, **extra):
    estado = conn.execute("SELECT estado FROM maquinas WHERE id = %s", (maquina_id,)).fetchone()["estado"]
    solicitudes = [dict(s) for s in conn.execute(
        f"""SELECT id, maquina_id, estado, disponible, tandas_totales, tandas_iniciadas
            FROM solicitudes WHERE maquina_id = %s AND estado IN {ACTIVAS} ORDER BY id""", (maquina_id,))]
    return prolog.consultar({"accion": accion, "maquina_id": maquina_id,
                             "estado_maquina": estado, "solicitudes": solicitudes, **extra})


def asignar_siguiente(conn, maquina_id):
    """Pregunta a Prolog quién sigue y deja su solicitud como AUTORIZADA."""
    r = _consultar(conn, "SIGUIENTE", maquina_id)
    if r.get("accion") != "AUTORIZAR":
        return
    s = conn.execute("SELECT id, estado, usuario_id FROM solicitudes WHERE id = %s",
                     (r["solicitud_id"],)).fetchone()
    if s["estado"] == "EN_ESPERA":
        conn.execute("UPDATE solicitudes SET estado = 'AUTORIZADA' WHERE id = %s", (s["id"],))
        notificar(conn, s["usuario_id"], s["id"],
                  f"Es tu turno en la {NOMBRES[maquina_id]}. Ve a la terminal e inicia tu ciclo.")


def actualizar_ciclos(conn):
    """Marca como terminados los ciclos cuyo tiempo ya pasó (sin hilos en segundo plano)."""
    ahora = _ahora()
    filas = conn.execute("""SELECT c.id, c.fecha_inicio, c.duracion_minutos, s.id AS sid,
                                   s.usuario_id, s.maquina_id
                            FROM ciclos c JOIN solicitudes s ON s.id = c.solicitud_id
                            WHERE c.estado = 'EN_CURSO'""").fetchall()
    for f in filas:
        fin = _fecha(f["fecha_inicio"]) + timedelta(minutes=f["duracion_minutos"])
        if fin <= ahora:
            conn.execute("UPDATE ciclos SET estado = 'PENDIENTE_RETIRO', fecha_fin = %s WHERE id = %s",
                         (_texto(fin), f["id"]))
            conn.execute("UPDATE maquinas SET estado = 'PENDIENTE_RETIRO' WHERE id = %s", (f["maquina_id"],))
            notificar(conn, f["usuario_id"], f["sid"],
                      f"Tu tanda en la {NOMBRES[f['maquina_id']]} terminó. Retira tu ropa.")


# ------------------------------------------------------------------ solicitudes
def _cola(conn, maquina_id):
    filas = conn.execute(
        f"""SELECT s.id, s.estado, s.disponible, s.tandas_totales, s.tandas_iniciadas, u.nombre
            FROM solicitudes s JOIN usuarios u ON u.id = s.usuario_id
            WHERE s.maquina_id = %s AND s.estado IN {ACTIVAS}
            ORDER BY (s.estado = 'EN_USO') DESC, s.id""", (maquina_id,)).fetchall()
    return [{"posicion": i + 1, "solicitud_id": f["id"], "nombre": f["nombre"], "estado": f["estado"],
             "disponible": bool(f["disponible"]), "tandas_totales": f["tandas_totales"],
             "tandas_iniciadas": f["tandas_iniciadas"]} for i, f in enumerate(filas)]


def crear_solicitud(conn, usuario_id, maquina_id, tandas):
    if conn.execute(f"SELECT 1 FROM solicitudes WHERE usuario_id = %s AND maquina_id = %s AND estado IN {ACTIVAS}",
                    (usuario_id, maquina_id)).fetchone():
        raise ErrorNegocio(f"Ya tienes una solicitud activa para la {NOMBRES[maquina_id]}", 409)
    sid = conn.execute("INSERT INTO solicitudes (usuario_id, maquina_id, tandas_totales) VALUES (%s,%s,%s) RETURNING id",
                       (usuario_id, maquina_id, tandas)).fetchone()["id"]
    asignar_siguiente(conn, maquina_id)
    return _mi_solicitud(conn, sid)


def _mi_solicitud(conn, sid):
    s = conn.execute("""SELECT s.*, m.tipo FROM solicitudes s JOIN maquinas m ON m.id = s.maquina_id
                        WHERE s.id = %s""", (sid,)).fetchone()
    pos = next((c["posicion"] for c in _cola(conn, s["maquina_id"]) if c["solicitud_id"] == sid), None)
    return {"id": s["id"], "maquina_id": s["maquina_id"], "maquina": s["tipo"], "estado": s["estado"],
            "disponible": bool(s["disponible"]), "tandas_totales": s["tandas_totales"],
            "tandas_iniciadas": s["tandas_iniciadas"], "posicion": pos}


def solicitudes_de(conn, usuario_id):
    ids = conn.execute(f"SELECT id FROM solicitudes WHERE usuario_id = %s AND estado IN {ACTIVAS} ORDER BY id",
                       (usuario_id,)).fetchall()
    return [_mi_solicitud(conn, r["id"]) for r in ids]


def _propia(conn, usuario_id, sid):
    s = conn.execute("SELECT * FROM solicitudes WHERE id = %s AND usuario_id = %s", (sid, usuario_id)).fetchone()
    if not s:
        raise ErrorNegocio("Solicitud no encontrada", 404)
    return s


def cancelar(conn, usuario_id, sid):
    s = _propia(conn, usuario_id, sid)
    maquina = conn.execute("SELECT estado FROM maquinas WHERE id = %s", (s["maquina_id"],)).fetchone()["estado"]
    if s["estado"] in ("EN_ESPERA", "AUTORIZADA"):
        pass
    elif s["estado"] == "EN_USO" and maquina == "ENTRE_TANDAS":
        conn.execute("UPDATE maquinas SET estado = 'LIBRE' WHERE id = %s", (s["maquina_id"],))
    else:
        raise ErrorNegocio("No se puede cancelar un turno con un ciclo en curso", 409)
    estado = "CANCELADA" if s["estado"] != "EN_USO" else "FINALIZADA"
    conn.execute("UPDATE solicitudes SET estado = %s, fecha_finalizacion = CURRENT_TIMESTAMP WHERE id = %s",
                 (estado, sid))
    asignar_siguiente(conn, s["maquina_id"])


def cambiar_disponibilidad(conn, usuario_id, sid, disponible):
    s = _propia(conn, usuario_id, sid)
    if s["estado"] not in ("EN_ESPERA", "AUTORIZADA"):
        raise ErrorNegocio("Solo puedes cambiar la disponibilidad mientras esperas turno", 409)
    nuevo = "EN_ESPERA" if (not disponible and s["estado"] == "AUTORIZADA") else s["estado"]
    conn.execute("UPDATE solicitudes SET disponible = %s, estado = %s WHERE id = %s", (int(disponible), nuevo, sid))
    asignar_siguiente(conn, s["maquina_id"])


# ------------------------------------------------------------------ ciclos
def _solicitud_activa(conn, usuario_id, maquina_id):
    s = conn.execute(f"SELECT * FROM solicitudes WHERE usuario_id = %s AND maquina_id = %s AND estado IN {ACTIVAS}",
                     (usuario_id, maquina_id)).fetchone()
    if not s:
        raise ErrorNegocio(f"No tienes una solicitud activa para la {NOMBRES[maquina_id]}", 404)
    return s


def iniciar_ciclo(conn, usuario_id, maquina_id, minutos):
    s = _solicitud_activa(conn, usuario_id, maquina_id)
    n = s["tandas_iniciadas"] + 1
    if n > s["tandas_totales"]:
        raise ErrorNegocio("Ya iniciaste todas tus tandas", 409)
    r = _consultar(conn, "INICIAR", maquina_id, solicitud_id=s["id"], numero_tanda=n)
    if not r.get("permitido"):
        raise ErrorNegocio("Aún no es tu turno o la máquina está ocupada", 409)
    conn.execute("INSERT INTO ciclos (solicitud_id, numero_tanda, duracion_minutos) VALUES (%s,%s,%s)",
                 (s["id"], n, minutos))
    conn.execute("UPDATE solicitudes SET tandas_iniciadas = %s, estado = 'EN_USO' WHERE id = %s", (n, s["id"]))
    conn.execute("UPDATE maquinas SET estado = 'EN_USO' WHERE id = %s", (maquina_id,))
    return {"tanda": n, "tandas_totales": s["tandas_totales"], "minutos": minutos}


def retirar(conn, usuario_id, maquina_id):
    s = conn.execute("SELECT * FROM solicitudes WHERE usuario_id = %s AND maquina_id = %s AND estado = 'EN_USO'",
                     (usuario_id, maquina_id)).fetchone()
    if not s:
        raise ErrorNegocio("No tienes una tanda en esta máquina", 404)
    r = _consultar(conn, "RETIRAR", maquina_id, solicitud_id=s["id"])
    if not r.get("permitido"):
        raise ErrorNegocio("Tu tanda aún no termina", 409)
    conn.execute("""UPDATE ciclos SET estado = 'RETIRADO', fecha_retiro = CURRENT_TIMESTAMP
                    WHERE solicitud_id = %s AND estado = 'PENDIENTE_RETIRO'""", (s["id"],))
    if r["resultado"] == "CONTINUAR_TANDAS":
        conn.execute("UPDATE maquinas SET estado = 'ENTRE_TANDAS' WHERE id = %s", (maquina_id,))
        return {"resultado": "CONTINUAR_TANDAS", "mensaje": "Tanda retirada. Puedes iniciar la siguiente."}
    conn.execute("UPDATE solicitudes SET estado = 'FINALIZADA', fecha_finalizacion = CURRENT_TIMESTAMP WHERE id = %s",
                 (s["id"],))
    conn.execute("UPDATE maquinas SET estado = 'LIBRE' WHERE id = %s", (maquina_id,))
    asignar_siguiente(conn, maquina_id)
    return {"resultado": "LIBERAR_MAQUINA", "mensaje": "Ropa retirada. La máquina quedó libre."}


# ------------------------------------------------------------------ estado público
def estado_general(conn):
    maquinas = []
    for m in conn.execute("SELECT id, tipo, estado FROM maquinas ORDER BY id"):
        cola = _cola(conn, m["id"])
        ocupante = next((c for c in cola if c["estado"] == "EN_USO"), None)
        restantes = None
        if m["estado"] == "EN_USO":
            c = conn.execute("""SELECT c.fecha_inicio, c.duracion_minutos FROM ciclos c
                                JOIN solicitudes s ON s.id = c.solicitud_id
                                WHERE s.maquina_id = %s AND c.estado = 'EN_CURSO' ORDER BY c.id DESC LIMIT 1""",
                             (m["id"],)).fetchone()
            if c:
                fin = _fecha(c["fecha_inicio"]) + timedelta(minutes=c["duracion_minutos"])
                restantes = max(0, int((fin - _ahora()).total_seconds()))
        maquinas.append({"id": m["id"], "tipo": m["tipo"], "estado": m["estado"],
                         "ocupante": ocupante, "segundos_restantes": restantes, "cola": cola})
    return {"maquinas": maquinas}


def notificaciones(conn, usuario_id, limite=20):
    filas = conn.execute("""SELECT id, mensaje, leida, fecha FROM notificaciones
                            WHERE usuario_id = %s ORDER BY id DESC LIMIT %s""", (usuario_id, limite)).fetchall()
    return [{**dict(f), "leida": bool(f["leida"])} for f in filas]
