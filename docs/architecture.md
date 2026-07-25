# Architecture

```text
Client --HTTP(Bearer JWT)--> API (FastAPI) --SQL--> PostgreSQL
```

One API service, one relational database, no shared session store — JWT is stateless by design (`ADR-RP01`). No message queue, no cache, no second service: `requirements.md` OUT explicitly excludes rate limiting, webhooks and multi-tenant, so none of them are justified here.

## Layering inside the API

```text
routers/      -> HTTP concerns only (parsing, status codes)
deps.py       -> JWT verification (Paso 5) - the only place that decodes a Bearer token
services/     -> business rules (ownership check, soft delete, JWT issuance/refresh)
repositories/ -> persistence (SQLAlchemy), one per entity (Usuario, Tarea)
models/       -> SQLAlchemy models, mapped 1:1 to db/schema.sql (M1) - no re-declared constraints
schemas/      -> Pydantic request/response models
security.py   -> password hashing (bcrypt) and JWT encode/decode primitives
```

A router never talks to a repository directly — it goes through a service, so the ownership check (`TareaService.obtener_autorizada`) lives in exactly one place, never duplicated per endpoint. `deps.py` is the single point that turns a raw `Authorization` header into a trusted `usuario_id`; nothing downstream re-validates a token.

## Authentication and authorization, kept as two separate concerns

- **Authentication** (`src/deps.py`, `get_current_user_id`): is this a real, unexpired, correctly-signed JWT of type `"access"`? Failure → `401`. Never touches the database.
- **Authorization** (`src/services.py`, `TareaService.obtener_autorizada`): does this already-authenticated user own this specific task? Failure → `403`. Always touches the database (needs the task's `propietario_id`).

Keeping these as two distinct functions, never merged, is what makes `ADR-RP02` (401 vs. 403 as genuinely different failures) enforceable in code, not just in the contract.

## What this deliberately does not include

- No refresh-token revocation list / no session store — `ADR-RP03`: accepted trade-off, no rotation.
- No RBAC, no roles — already fixed by `requirements.md` (OUT) before this project started, not a decision made here; ownership is the only authorization model this project demonstrates (`docs/decisions.md`, "Restricciones ya fijadas por la especificación").
- No rate limiting, no API keys, no OAuth social login — out of scope (`requirements.md` OUT).
