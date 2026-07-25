import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# --- Auth / Usuario ---

class UsuarioRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Tarea ---

class TareaCreate(BaseModel):
    titulo: str = Field(min_length=1)
    descripcion: str = ""
    estado: Optional[str] = None


class TareaUpdate(BaseModel):
    titulo: str = Field(min_length=1)
    descripcion: str = ""
    estado: str


class TareaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    titulo: str
    descripcion: str
    estado: str
    propietario_id: uuid.UUID


class TareaListOut(BaseModel):
    items: list[TareaOut]
    total: int
    page: int
    limit: int


class TareaDeletedOut(BaseModel):
    id: uuid.UUID
    eliminado_en: str
