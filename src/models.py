import uuid

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship

from src.database import Base

# db/schema.sql (M1) is the single authoritative DDL - produced by
# 01_Disenar_Base_Datos and verified in db/VERIFICATION.md. These ORM models
# map to those tables; they deliberately do NOT redeclare CHECK/UNIQUE
# constraints already enforced by the real schema, to avoid two sources of
# truth for the same rule (same reasoning already applied in 01_CRUD).

ESTADOS_VALIDOS = ("pendiente", "en_progreso", "completada")


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)

    tareas = relationship("Tarea", back_populates="propietario")


class Tarea(Base):
    __tablename__ = "tarea"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String, nullable=False)
    propietario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False
    )
    eliminado_en = Column(TIMESTAMP, nullable=True)

    propietario = relationship("Usuario", back_populates="tareas")
