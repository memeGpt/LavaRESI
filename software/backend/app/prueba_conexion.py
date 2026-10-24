
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
def verificar_conexion():
    return {
        "estado": "ok",
        "mensaje": "LavaRESI conectado"
    }
