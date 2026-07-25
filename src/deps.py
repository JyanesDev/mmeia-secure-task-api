import uuid

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.security import decode_token

# Paso 5 del Playbook: exige token valido antes de ejecutar cualquier endpoint
# de tareas. HTTPBearer ya responde 403 si falta la cabecera Authorization por
# completo; se normaliza explicitamente a 401 (FR6: "401 si no autenticado"),
# nunca dejar que el 403 generico del framework se confunda con el 403 de
# ownership (api/contrato.md).
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> uuid.UUID:
    if credentials is None:
        raise HTTPException(status_code=401, detail="falta token de autenticacion")
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="token invalido o expirado")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="token no es de tipo access")
    return uuid.UUID(payload["sub"])
