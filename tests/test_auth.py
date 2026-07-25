import jwt

from src.security import JWT_SECRET, JWT_ALGORITHM


def test_register_success(client):
    resp = client.post(
        "/api/v1/auth/register", json={"email": "ana@example.com", "password": "secret123"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "ana@example.com"
    assert "id" in body
    assert "password" not in body  # NFR3: password nunca en la respuesta


def test_register_invalid_email(client):
    resp = client.post(
        "/api/v1/auth/register", json={"email": "no-es-un-email", "password": "secret123"}
    )
    assert resp.status_code == 422


def test_register_duplicate_email(client, registered_user):
    email, _ = registered_user
    resp = client.post(
        "/api/v1/auth/register", json={"email": email, "password": "otraPassword"}
    )
    assert resp.status_code == 409


def test_login_success_returns_token_pair(client, registered_user):
    email, password = registered_user
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password(client, registered_user):
    email, _ = registered_user
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "incorrecta"})
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "nadie@example.com", "password": "x"}
    )
    assert resp.status_code == 401


def test_refresh_returns_new_access_token_without_password(client, registered_user):
    email, password = registered_user
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refresh_rejects_access_token_used_as_refresh(client, registered_user):
    """FR3/NFR4: un access_token no debe servir para refrescar - los tipos no se confunden."""
    email, password = registered_user
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access_token = login_resp.json()["access_token"]

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401


def test_refresh_rejects_garbage_token(client):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "no-es-un-jwt"})
    assert resp.status_code == 401


def test_access_token_expires_before_refresh_token(client, registered_user):
    """NFR4, verificado con evidencia real decodificando ambos JWT, no solo leyendo la constante."""
    email, password = registered_user
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    body = login_resp.json()

    access_payload = jwt.decode(body["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
    refresh_payload = jwt.decode(body["refresh_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])

    assert access_payload["exp"] < refresh_payload["exp"]
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
