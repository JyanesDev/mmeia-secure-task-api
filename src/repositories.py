import uuid

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import Usuario, Tarea


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, email: str, password_hash: str) -> Usuario:
        usuario = Usuario(email=email, password_hash=password_hash)
        self.db.add(usuario)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=409, detail="email ya registrado")
        self.db.refresh(usuario)
        return usuario

    def obtener_por_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def obtener(self, usuario_id: uuid.UUID) -> Usuario | None:
        return self.db.get(Usuario, usuario_id)


class TareaRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, **kwargs) -> Tarea:
        tarea = Tarea(**kwargs)
        self.db.add(tarea)
        self.db.commit()
        self.db.refresh(tarea)
        return tarea

    def obtener_activa(self, tarea_id: uuid.UUID) -> Tarea | None:
        """Nunca devuelve una tarea soft-deleted - se trata como inexistente (api/contrato.md)."""
        return (
            self.db.query(Tarea)
            .filter(Tarea.id == tarea_id, Tarea.eliminado_en.is_(None))
            .first()
        )

    def listar_de_propietario(
        self, propietario_id: uuid.UUID, page: int, limit: int, estado: str | None
    ) -> tuple[list[Tarea], int]:
        query = self.db.query(Tarea).filter(
            Tarea.propietario_id == propietario_id, Tarea.eliminado_en.is_(None)
        )
        if estado is not None:
            query = query.filter(Tarea.estado == estado)
        total = query.count()
        items = (
            query.order_by(Tarea.titulo)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return items, total

    def guardar(self, tarea: Tarea) -> Tarea:
        self.db.commit()
        self.db.refresh(tarea)
        return tarea
