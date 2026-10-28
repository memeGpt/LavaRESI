"""Hash de PIN/contraseña, sesiones firmadas y límite de intentos fallidos."""
import base64
import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque

from .config import SECRETO, SESION_HORAS

ITER_PIN = 10_000        # el PIN es de 4 dígitos: se verifica contra todos los usuarios
ITER_PASSWORD = 200_000


def hashear(valor: str, iteraciones: int) -> str:
    sal = secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", valor.encode(), sal.encode(), iteraciones).hex()
    return f"pbkdf2${iteraciones}${sal}${h}"


def verificar(valor: str, guardado: str) -> bool:
    try:
        _, it, sal, h = guardado.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", valor.encode(), sal.encode(), int(it)).hex()
        return hmac.compare_digest(calc, h)
    except ValueError:
        return False


# ---- Sesión web: cookie "usuario_id.expira.firma" ----
def crear_token(usuario_id: int) -> str:
    carga = f"{usuario_id}.{int(time.time()) + SESION_HORAS * 3600}"
    firma = hmac.new(SECRETO, carga.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{carga}.{firma}".encode()).decode()


def leer_token(token: str | None) -> int | None:
    if not token:
        return None
    try:
        usuario_id, expira, firma = base64.urlsafe_b64decode(token.encode()).decode().split(".")
        carga = f"{usuario_id}.{expira}"
        esperada = hmac.new(SECRETO, carga.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(firma, esperada) and int(expira) > time.time():
            return int(usuario_id)
    except Exception:
        pass
    return None


# ---- Límite de intentos fallidos por IP (protege el PIN de 4 dígitos) ----
class LimiteIntentos:
    def __init__(self, maximo=10, ventana=60):
        self.maximo, self.ventana = maximo, ventana
        self.fallos = defaultdict(deque)

    def _limpiar(self, clave):
        q = self.fallos[clave]
        while q and q[0] < time.time() - self.ventana:
            q.popleft()
        return q

    def bloqueado(self, clave) -> bool:
        return len(self._limpiar(clave)) >= self.maximo

    def registrar_fallo(self, clave):
        self._limpiar(clave).append(time.time())


limite = LimiteIntentos()
