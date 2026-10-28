"""Cuerpos de las peticiones (validación con Pydantic)."""
from pydantic import BaseModel, Field

PIN = Field(pattern=r"^\d{4}$", description="PIN de 4 dígitos")


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=60)
    usuario: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_.-]+$")
    pin: str = PIN
    password: str = Field(min_length=6, max_length=100)


class LoginIn(BaseModel):
    usuario: str
    password: str


class SolicitudWebIn(BaseModel):
    maquina_id: int = Field(ge=1, le=2)
    tandas: int = Field(ge=1, le=3)


class DisponibilidadIn(BaseModel):
    disponible: bool


class SolicitudTerminalIn(SolicitudWebIn):
    pin: str = PIN


class IniciarIn(BaseModel):
    pin: str = PIN
    maquina_id: int = Field(ge=1, le=2)
    minutos: int = Field(ge=1, le=180)


class RetirarIn(BaseModel):
    pin: str = PIN
    maquina_id: int = Field(ge=1, le=2)


class MiTurnoIn(BaseModel):
    pin: str = PIN
