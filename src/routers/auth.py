from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas import (
    UsuarioRegister,
    UsuarioOut,
    LoginRequest,
    TokenPairOut,
    RefreshRequest,
    AccessTokenOut,
)
from src.services import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioOut, status_code=201)
def register(payload: UsuarioRegister, db: Session = Depends(get_db)):
    return AuthService(db).registrar(email=payload.email, password=payload.password)


@router.post("/login", response_model=TokenPairOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    access_token, refresh_token = AuthService(db).login(payload.email, payload.password)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh", response_model=AccessTokenOut)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    access_token = AuthService(db).refrescar(payload.refresh_token)
    return {"access_token": access_token}
