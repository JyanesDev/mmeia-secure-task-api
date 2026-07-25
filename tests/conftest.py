import pathlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app

TEST_DATABASE_URL = "postgresql+psycopg://postgres:test@localhost:5432/taskapi_test"
SCHEMA_PATH = pathlib.Path(__file__).resolve().parent.parent / "db" / "schema.sql"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def apply_schema():
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS tarea, usuario CASCADE"))
        conn.execute(text(SCHEMA_PATH.read_text()))
    yield


@pytest.fixture(autouse=True)
def clean_tables():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE tarea, usuario CASCADE"))
    yield


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Devuelve (email, password) de un usuario ya registrado."""
    email, password = "ana@example.com", "password123"
    resp = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 201
    return email, password


@pytest.fixture
def auth_headers(client, registered_user):
    """Cabecera Authorization con un access_token real de un usuario ya logueado."""
    email, password = registered_user
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers(client):
    """Cabecera Authorization de un SEGUNDO usuario, distinto del de auth_headers."""
    email, password = "otro@example.com", "otraPassword456"
    resp = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 201
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
