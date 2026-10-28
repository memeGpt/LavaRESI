"""Configuración central de LavaRESI (se puede ajustar con variables de entorno)."""
import os
import secrets
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]          # software/backend
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SCHEMA_PATH = RAIZ / "database" / "schema.sql"
PROLOG_PATH = RAIZ / "prolog" / "reglas_turnos.pl"
FRONTEND_PATH = RAIZ.parent / "frontend"

# Clave opcional que debe enviar el ESP32 en el header X-Terminal-Key.
# Si no se define, los endpoints de la terminal quedan abiertos (útil para pruebas).
TERMINAL_KEY = os.getenv("LAVARESI_TERMINAL_KEY", "")

SESION_HORAS = 12


def _cargar_secreto() -> bytes:
    """Clave para firmar las sesiones web. Se guarda en .secreto (ignorado por git)."""
    env = os.getenv("LAVARESI_SECRET")
    if env:
        return env.encode()
    archivo = RAIZ / ".secreto"
    if not archivo.exists():
        archivo.write_text(secrets.token_hex(32))
    return archivo.read_text().strip().encode()


SECRETO = _cargar_secreto()
