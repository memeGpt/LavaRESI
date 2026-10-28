"""Acceso a PostgreSQL para LavaRESI."""
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from .config import DATABASE_URL, SCHEMA_PATH


def conectar():
    if not DATABASE_URL:
        raise RuntimeError(
            "Falta la variable de entorno DATABASE_URL. Configúrala con la cadena de conexión de Neon."
        )
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


@contextmanager
def transaccion():
    """Abre una transacción; confirma si termina bien y revierte si hay error."""
    with conectar() as conn:
        # Serializa las operaciones de negocio para mantener consistente la cola.
        conn.execute("SELECT pg_advisory_xact_lock(76843021)")
        yield conn


def inicializar():
    """Crea las tablas e índices si no existen y carga las máquinas iniciales."""
    contenido = SCHEMA_PATH.read_text(encoding="utf-8")
    with conectar() as conn:
        for sentencia in contenido.split(";"):
            sentencia = sentencia.strip()
            if sentencia:
                conn.execute(sentencia)
