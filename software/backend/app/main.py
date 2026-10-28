"""LavaRESI - API y página web.
Ejecutar desde software/backend:
    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_PATH
from .db import inicializar
from .rutas import publico, terminal, web
from .servicios.turnos import ErrorNegocio


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    inicializar()
    yield


app = FastAPI(title="LavaRESI", lifespan=ciclo_de_vida)


@app.exception_handler(ErrorNegocio)
async def manejar_error_negocio(request: Request, exc: ErrorNegocio):
    return JSONResponse(status_code=exc.codigo, content={"detail": exc.mensaje})


app.include_router(publico.router)
app.include_router(terminal.router)
app.include_router(web.router)

# La página web (frontend) la sirve el mismo servidor.
app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")
