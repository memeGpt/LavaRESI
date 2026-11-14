"""Acceso a PostgreSQL (Neon) para LavaRESI.

CAMBIO IMPORTANTE: antes cada petición abría una conexión nueva a Neon
(unos 1-2 s desde Costa Rica). Ahora se reutilizan conexiones con un pool.
"""
import threading
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .config import DATABASE_URL, SCHEMA_PATH

_pool: ConnectionPool | None = None
_candado_pool = threading.Lock()


def _verificar_url():
    if not DATABASE_URL:
        raise RuntimeError(
            "Falta la variable de entorno DATABASE_URL. Configúrala con la cadena de conexión de Neon."
        )


def conectar():
    """Conexión suelta (solo para inicializar la base y scripts)."""
    _verificar_url()
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def obtener_pool() -> ConnectionPool:
    """Crea el pool la primera vez y lo reutiliza después."""
    global _pool
    if _pool is None:
        with _candado_pool:
            if _pool is None:
                _verificar_url()
                pool = ConnectionPool(
                    DATABASE_URL,
                    min_size=2,            # conexiones siempre listas
                    max_size=10,
                    max_idle=240,          # cierra las que llevan 4 min sin uso
                    kwargs={"row_factory": dict_row, "prepare_threshold": None},
                    check=ConnectionPool.check_connection,  # descarta conexiones muertas (Neon dormido)
                    open=False,
                )
                pool.open(wait=True, timeout=30)
                _pool = pool
    return _pool


def cerrar_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def transaccion():
    """Transacción que ESCRIBE: confirma si termina bien y revierte si hay error.
    Usa un candado global para mantener consistente la cola de turnos."""
    with obtener_pool().connection() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(76843021)")
        yield conn


@contextmanager
def lectura():
    """Consulta SOLO LECTURA: no toma el candado global, así no hace esperar
    a quien está pidiendo o cancelando un turno."""
    with obtener_pool().connection() as conn:
        yield conn


def inicializar():
    """Crea las tablas e índices si no existen y carga las máquinas iniciales."""
    contenido = SCHEMA_PATH.read_text(encoding="utf-8")
    with conectar() as conn:
        for sentencia in contenido.split(";"):
            sentencia = sentencia.strip()
            if sentencia:
                conn.execute(sentencia)