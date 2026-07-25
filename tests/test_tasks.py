from datetime import datetime, timedelta, timezone

import jwt

from src.models import Tarea
from src.security import JWT_SECRET, JWT_ALGORITHM


def _crear_tarea(client, headers, titulo="Comprar leche", descripcion="", estado=None):
    payload = {"titulo": titulo, "descripcion": descripcion}
    if estado is not None:
        payload["estado"] = estado
    return client.post("/api/v1/tasks", json=payload, headers=headers)


# --- POST /api/v1/tasks ---

def test_create_task_without_token_is_401(client):
    resp = client.post("/api/v1/tasks", json={"titulo": "x", "descripcion": ""})
    assert resp.status_code == 401


def test_create_task_success(client, auth_headers):
    resp = _crear_tarea(client, auth_headers, titulo="Comprar leche", descripcion="2 litros")
    assert resp.status_code == 201
    body = resp.json()
    assert body["titulo"] == "Comprar leche"
    assert body["estado"] == "pendiente"  # default fijado en services.py, ver api/contrato.md
    assert "propietario_id" in body


def test_create_task_empty_titulo_is_400(client, auth_headers):
    resp = client.post(
        "/api/v1/tasks", json={"titulo": "", "descripcion": ""}, headers=auth_headers
    )
    assert resp.status_code == 422  # validacion de Pydantic (min_length=1) antes del servicio


def test_create_task_invalid_estado_is_400(client, auth_headers):
    resp = _crear_tarea(client, auth_headers, estado="archivada")
    assert resp.status_code == 400


# --- GET /api/v1/tasks ---

def test_list_tasks_without_token_is_401(client):
    resp = client.get("/api/v1/tasks")
    assert resp.status_code == 401


def test_list_tasks_only_shows_own(client, auth_headers, other_user_headers):
    _crear_tarea(client, auth_headers, titulo="Tarea de Ana")
    _crear_tarea(client, other_user_headers, titulo="Tarea de Otro")

    resp = client.get("/api/v1/tasks", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["titulo"] == "Tarea de Ana"


def test_list_tasks_respects_limit(client, auth_headers):
    for i in range(5):
        _crear_tarea(client, auth_headers, titulo=f"Tarea {i}")

    resp = client.get("/api/v1/tasks?limit=2", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["total"] == 5


def test_list_tasks_filters_by_status(client, auth_headers):
    _crear_tarea(client, auth_headers, titulo="Pendiente", estado="pendiente")
    _crear_tarea(client, auth_headers, titulo="En progreso", estado="en_progreso")

    resp = client.get("/api/v1/tasks?status=en_progreso", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["titulo"] == "En progreso"


# --- GET /api/v1/tasks/{id} ---

def test_get_task_without_token_is_401(client, auth_headers):
    tarea = _crear_tarea(client, auth_headers).json()
    resp = client.get(f"/api/v1/tasks/{tarea['id']}")
    assert resp.status_code == 401


def test_get_task_not_found_is_404(client, auth_headers):
    resp = client.get("/api/v1/tasks/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404


def test_get_task_of_another_user_is_403_and_leaks_nothing(client, auth_headers, other_user_headers):
    """FR6 (403, no 401 ni 404) + NFR5 (la respuesta 403 no debe revelar datos de la tarea ajena)."""
    tarea_ajena = _crear_tarea(client, other_user_headers, titulo="Secreto de otro").json()

    resp = client.get(f"/api/v1/tasks/{tarea_ajena['id']}", headers=auth_headers)
    assert resp.status_code == 403
    body_text = resp.text
    assert "Secreto de otro" not in body_text


def test_get_task_success(client, auth_headers):
    tarea = _crear_tarea(client, auth_headers, titulo="Mi tarea").json()
    resp = client.get(f"/api/v1/tasks/{tarea['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["titulo"] == "Mi tarea"


# --- PUT /api/v1/tasks/{id} ---

def test_put_task_without_token_is_401(client, auth_headers):
    tarea = _crear_tarea(client, auth_headers).json()
    resp = client.put(
        f"/api/v1/tasks/{tarea['id']}",
        json={"titulo": "x", "descripcion": "", "estado": "pendiente"},
    )
    assert resp.status_code == 401


def test_put_task_not_found_is_404(client, auth_headers):
    resp = client.put(
        "/api/v1/tasks/00000000-0000-0000-0000-000000000000",
        json={"titulo": "x", "descripcion": "", "estado": "pendiente"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_put_task_of_another_user_is_403(client, auth_headers, other_user_headers):
    tarea_ajena = _crear_tarea(client, other_user_headers).json()
    resp = client.put(
        f"/api/v1/tasks/{tarea_ajena['id']}",
        json={"titulo": "hackeado", "descripcion": "", "estado": "pendiente"},
        headers=auth_headers,
    )
    assert resp.status_code == 403


def test_put_task_invalid_estado_is_400(client, auth_headers):
    tarea = _crear_tarea(client, auth_headers).json()
    resp = client.put(
        f"/api/v1/tasks/{tarea['id']}",
        json={"titulo": "x", "descripcion": "", "estado": "no_valido"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_put_task_success(client, auth_headers):
    tarea = _crear_tarea(client, auth_headers, titulo="Original").json()
    resp = client.put(
        f"/api/v1/tasks/{tarea['id']}",
        json={"titulo": "Editada", "descripcion": "nueva desc", "estado": "en_progreso"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["titulo"] == "Editada"
    assert body["estado"] == "en_progreso"


# --- DELETE /api/v1/tasks/{id} (soft delete) ---

def test_delete_task_without_token_is_401(client, auth_headers):
    tarea = _crear_tarea(client, auth_headers).json()
    resp = client.delete(f"/api/v1/tasks/{tarea['id']}")
    assert resp.status_code == 401


def test_delete_task_not_found_is_404(client, auth_headers):
    resp = client.delete(
        "/api/v1/tasks/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert resp.status_code == 404


def test_delete_task_of_another_user_is_403(client, auth_headers, other_user_headers):
    tarea_ajena = _crear_tarea(client, other_user_headers).json()
    resp = client.delete(f"/api/v1/tasks/{tarea_ajena['id']}", headers=auth_headers)
    assert resp.status_code == 403


def test_delete_task_is_soft_delete_not_physical(client, auth_headers, db_session):
    """FR5: nunca DELETE fisico - la fila debe seguir existiendo en la tabla tras el borrado."""
    tarea = _crear_tarea(client, auth_headers, titulo="A borrar").json()

    resp = client.delete(f"/api/v1/tasks/{tarea['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["eliminado_en"] is not None

    fila = db_session.query(Tarea).filter(Tarea.id == tarea["id"]).first()
    assert fila is not None  # la fila sigue ahi - nunca un DELETE fisico
    assert fila.eliminado_en is not None


def test_get_deleted_task_returns_404_even_for_owner(client, auth_headers):
    """Una tarea soft-deleted se trata como inexistente para cualquiera, incluido el dueno."""
    tarea = _crear_tarea(client, auth_headers, titulo="A borrar").json()
    client.delete(f"/api/v1/tasks/{tarea['id']}", headers=auth_headers)

    resp = client.get(f"/api/v1/tasks/{tarea['id']}", headers=auth_headers)
    assert resp.status_code == 404


def test_deleted_task_excluded_from_listing(client, auth_headers):
    tarea = _crear_tarea(client, auth_headers, titulo="A borrar").json()
    client.delete(f"/api/v1/tasks/{tarea['id']}", headers=auth_headers)

    resp = client.get("/api/v1/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


# --- tasks.md M2: "access token expirado" (caso explicito del alcance) ---

def test_expired_access_token_is_401(client, registered_user):
    """`tasks.md` M2 exige un test explicito de access token expirado, no solo invalido."""
    email, password = registered_user
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access_token = login_resp.json()["access_token"]

    # Fabricado con el mismo secreto/algoritmo reales, pero con "exp" ya en el pasado -
    # no es un mock del verificador, es un JWT real que decode_token() rechazara por expirado.
    payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    now = datetime.now(timezone.utc)
    expired_payload = {**payload, "iat": now - timedelta(minutes=30), "exp": now - timedelta(minutes=15)}
    expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    resp = client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401


# --- Feature 5 / FR10: OpenAPI accesible sin autenticacion ---

def test_openapi_json_accessible_without_auth(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200


def test_docs_accessible_without_auth(client):
    resp = client.get("/docs")
    assert resp.status_code == 200
