import uuid
from datetime import datetime, timezone

import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models import ESTADOS_VALIDOS
from src.repositories import UsuarioRepository, TareaRepository
from src.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthService:
    def __init__(self, db: Session):
        self.usuarios = UsuarioRepository(db)

    def registrar(self, email: str, password: str):
        return self.usuarios.crear(email=email, password_hash=hash_password(password))

    def login(self, email: str, password: str) -> tuple[str, str]:
        usuario = self.usuarios.obtener_por_email(email)
        if usuario is None or not verify_password(password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="email o password incorrectos")
        return create_access_token(str(usuario.id)), create_refresh_token(str(usuario.id))

    def refrescar(self, refresh_token: str) -> str:
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="refresh_token invalido o expirado")
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="token no es de tipo refresh")
        return create_access_token(payload["sub"])


class TareaService:
    MAX_LIMIT = 100

    def __init__(self, db: Session):
        self.tareas = TareaRepository(db)

    def crear(self, propietario_id: uuid.UUID, titulo: str, descripcion: str, estado: str | None):
        estado_final = estado if estado is not None else "pendiente"
        if estado_final not in ESTADOS_VALIDOS:
            raise HTTPException(status_code=400, detail=f"estado invalido: {estado_final}")
        return self.tareas.crear(
            titulo=titulo,
            descripcion=descripcion,
            estado=estado_final,
            propietario_id=propietario_id,
        )

    def obtener_autorizada(self, tarea_id: uuid.UUID, usuario_id: uuid.UUID):
        """404 si no existe/soft-deleted; 403 solo si existe activa y pertenece a otro (FR6, NFR5)."""
        tarea = self.tareas.obtener_activa(tarea_id)
        if tarea is None:
            raise HTTPException(status_code=404, detail="tarea no encontrada")
        if tarea.propietario_id != usuario_id:
            raise HTTPException(status_code=403, detail="no autorizado")
        return tarea

    def listar(self, propietario_id: uuid.UUID, page: int, limit: int, estado: str | None):
        if estado is not None and estado not in ESTADOS_VALIDOS:
            raise HTTPException(status_code=400, detail=f"estado invalido: {estado}")
        limit = min(limit, self.MAX_LIMIT)
        items, total = self.tareas.listar_de_propietario(propietario_id, page, limit, estado)
        return items, total, page, limit

    def actualizar(self, tarea_id: uuid.UUID, usuario_id: uuid.UUID, titulo: str, descripcion: str, estado: str):
        if estado not in ESTADOS_VALIDOS:
            raise HTTPException(status_code=400, detail=f"estado invalido: {estado}")
        tarea = self.obtener_autorizada(tarea_id, usuario_id)
        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.estado = estado
        return self.tareas.guardar(tarea)

    def eliminar(self, tarea_id: uuid.UUID, usuario_id: uuid.UUID):
        tarea = self.obtener_autorizada(tarea_id, usuario_id)
        tarea.eliminado_en = datetime.now(timezone.utc)
        return self.tareas.guardar(tarea)
