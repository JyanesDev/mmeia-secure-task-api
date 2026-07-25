import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.deps import get_current_user_id
from src.schemas import TareaCreate, TareaUpdate, TareaOut, TareaListOut, TareaDeletedOut
from src.services import TareaService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("", response_model=TareaOut, status_code=201)
def crear_tarea(
    payload: TareaCreate,
    usuario_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return TareaService(db).crear(
        propietario_id=usuario_id,
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        estado=payload.estado,
    )


@router.get("", response_model=TareaListOut)
def listar_tareas(
    status: str | None = None,
    page: int = 1,
    limit: int = 20,
    usuario_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    items, total, page, limit = TareaService(db).listar(usuario_id, page, limit, status)
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/{tarea_id}", response_model=TareaOut)
def obtener_tarea(
    tarea_id: uuid.UUID,
    usuario_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return TareaService(db).obtener_autorizada(tarea_id, usuario_id)


@router.put("/{tarea_id}", response_model=TareaOut)
def actualizar_tarea(
    tarea_id: uuid.UUID,
    payload: TareaUpdate,
    usuario_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return TareaService(db).actualizar(
        tarea_id, usuario_id, payload.titulo, payload.descripcion, payload.estado
    )


@router.delete("/{tarea_id}", response_model=TareaDeletedOut)
def eliminar_tarea(
    tarea_id: uuid.UUID,
    usuario_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    tarea = TareaService(db).eliminar(tarea_id, usuario_id)
    return {"id": tarea.id, "eliminado_en": tarea.eliminado_en.isoformat()}
