"""Acceso a SQLite. Cada petición usa una transacción BEGIN IMMEDIATE para
evitar que dos peticiones simultáneas (ESP32 + web) se pisen entre sí."""
import sqlite3
from contextlib import contextmanager

from .config import DB_PATH, SCHEMA_PATH


def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaccion():
    conn = conectar()
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def inicializar():
    """Crea las tablas si no existen (usa el schema.sql del proyecto)."""
    conn = conectar()
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    finally:
        conn.close()
