import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# NFR4: el access_token debe tener una vida inferior a la del refresh_token.
# Ninguna FR/NFR fija la duracion exacta - valores de ingenieria razonables,
# no derivados de una regla de negocio especifica.
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

JWT_SECRET = os.environ.get(
    "JWT_SECRET", "dev-only-fallback-secret-never-use-in-production-32b"
)
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _create_token(subject: str, token_type: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_access_token(subject: str) -> str:
    return _create_token(subject, "access", ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(subject: str) -> str:
    return _create_token(subject, "refresh", REFRESH_TOKEN_EXPIRE_MINUTES)


def decode_token(token: str) -> dict:
    """Raises jwt.PyJWTError (ExpiredSignatureError, InvalidTokenError, ...) on failure."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
