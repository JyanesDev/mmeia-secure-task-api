# API verification (Playbook Paso 6, tabla adaptada y ampliada)

Ejecutado de verdad, no simulado: 36 tests de `pytest` contra un contenedor PostgreSQL 16 real y desechable (`docker run --rm`, destruido después), más un smoke test adicional de arranque real del servidor (`uvicorn`) con peticiones `curl` reales contra 12 escenarios.

A diferencia de `01_CRUD` (que omitió el Paso 5 deliberadamente), esta unidad aplica JWT completo — la tabla de verificación se amplía respecto al ejemplo literal del Playbook (5 endpoints, 1 entidad) a los 8 endpoints reales de `api/contrato.md` (3 de autenticación + 5 de tareas), con la tríada 401/403/404 completa donde aplica (FR6/NFR2).

## Tabla de verificación (adaptada a los 8 endpoints reales)

| Endpoint | Válido | Body/valor inválido | Sin token | Ajeno (403) | Inexistente |
|---|---|---|---|---|---|
| `POST /api/v1/auth/register` | 201 ✅ | 422 (email inválido) ✅ | — | — | 409 (email duplicado) ✅ |
| `POST /api/v1/auth/login` | 200 ✅ | 401 (password incorrecta) ✅ | — | — | 401 (email inexistente) ✅ |
| `POST /api/v1/auth/refresh` | 200 ✅ | 401 (token de tipo access, o basura) ✅ | — | — | — |
| `POST /api/v1/tasks` | 201 ✅ | 400 (título vacío→422 Pydantic, estado inválido→400) ✅ | 401 ✅ | — | — |
| `GET /api/v1/tasks` | 200 ✅ (solo propias, `limit` respetado, filtro `status`) ✅ | — | 401 ✅ | — | — |
| `GET /api/v1/tasks/{id}` | 200 ✅ | — | 401 ✅ | 403 (sin filtrar datos, NFR5) ✅ | 404 ✅ |
| `PUT /api/v1/tasks/{id}` | 200 ✅ | 400 (estado inválido) ✅ | 401 ✅ | 403 ✅ | 404 ✅ |
| `DELETE /api/v1/tasks/{id}` | 200 ✅ (soft delete verificado — fila persiste, `eliminado_en` fijado) | — | 401 ✅ | 403 ✅ | 404 ✅ |

Adicional (regla derivada de `api/contrato.md`, no una celda de la tabla anterior): una tarea soft-deleted devuelve **404** incluso para su propio dueño (verificado explícitamente — `test_get_deleted_task_returns_404_even_for_owner`), y queda excluida del listado (`test_deleted_task_excluded_from_listing`). NFR4 (access_token expira antes que refresh_token) verificado decodificando ambos JWT reales, no solo leyendo la constante (`test_access_token_expires_before_refresh_token`). El caso explícito que `tasks.md` M2 pide literalmente ("access token expirado") se verifica con un JWT real fabricado con el mismo secreto/algoritmo pero `exp` ya en el pasado — no un mock del verificador (`test_expired_access_token_is_401`).

## Resultado real de la ejecución (pytest)

```
36 passed, 1 warning in 12.15s
```

El único warning restante es una `StarletteDeprecationWarning` de la librería (`httpx` con `starlette.testclient`), no relacionado con la lógica del proyecto — mismo tipo de advertencia benigna ya presente en la suite de `01_CRUD`.

**Hallazgo real corregido durante esta verificación (documentado, no silencioso):** la primera ejecución de la suite completa mostró `InsecureKeyLengthWarning: The HMAC key is 29 bytes long, which is below the minimum recommended length of 32 bytes for SHA256` — el secreto JWT de desarrollo por defecto (`src/security.py`) era demasiado corto. Corregido alargándolo a 32+ bytes; la suite se re-ejecutó limpia, sin ese warning. Relevante señalarlo explícitamente porque la seguridad es la tesis central de este proyecto: en un despliegue real, `JWT_SECRET` debe fijarse siempre por variable de entorno (nunca el valor por defecto), tarea de M3.

## Smoke test de arranque real (servidor vivo, no TestClient) — 12 escenarios

```
$ uvicorn src.main:app --port 8123
POST /api/v1/auth/register           → 201 {"id",...,"email"}
POST /api/v1/auth/login              → 200 {"access_token","refresh_token","token_type":"bearer"}
POST /api/v1/tasks (sin token)       → 401 {"detail":"falta token de autenticacion"}
POST /api/v1/tasks (con token)       → 201 {"id",...,"estado":"pendiente",...}
GET  /api/v1/tasks/{id}              → 200 (misma tarea)
GET  /api/v1/tasks/{id-inexistente}  → 404 {"detail":"tarea no encontrada"}
GET  /api/v1/tasks/{id-ajeno}        → 403 {"detail":"no autorizado"} (sin datos de la tarea ajena)
PUT  /api/v1/tasks/{id}              → 200 (titulo/estado actualizados)
DELETE /api/v1/tasks/{id}            → 200 {"id","eliminado_en":"2026-07-25T18:05:59..."}
GET  /api/v1/tasks/{id} (ya borrada) → 404 (incluso para el propio dueno)
POST /api/v1/auth/refresh            → 200 {"access_token",...} (nuevo, distinto del original)
GET  /openapi.json (sin token)       → 200 (Feature 5 / FR10)
```

Las 12 peticiones produjeron exactamente el código y comportamiento esperado.

Playbook Checklist final: 5/5 (adaptado a los 8 endpoints reales en vez de los 5 del ejemplo literal).

**Date:** 2026-07-25. **Stack:** FastAPI 0.139.2, SQLAlchemy 2.0.51, PyJWT 2.11.0, bcrypt 5.0.0, PostgreSQL 16.
