"""Inicializa las tablas PostgreSQL de LavaRESI.

Uso (desde software/backend):
    python database/inicializar_db.py
    python database/inicializar_db.py --demo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import inicializar, transaccion  # noqa: E402
from app.servicios.turnos import registrar_usuario  # noqa: E402

DEMO = [("Melissa", "melissa", "1234"), ("Kelvin", "kelvin", "2345"),
        ("Andy", "andy", "3456"), ("Andrei", "andrei", "4567")]

if __name__ == "__main__":
    inicializar()
    print("Base de datos PostgreSQL lista.")
    if "--demo" in sys.argv:
        with transaccion() as conn:
            for nombre, usuario, pin in DEMO:
                if not conn.execute("SELECT 1 FROM usuarios WHERE usuario = %s", (usuario,)).fetchone():
                    registrar_usuario(conn, nombre, usuario, pin, "lavaresi123")
        print("Usuarios demo creados (contraseña: lavaresi123)")
