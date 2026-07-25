# Contrato de la API

Producido siguiendo `04_Playbooks/02_Crear_API/PLAYBOOK.md` (Pasos 1-2). Cada endpoint corresponde a una operación real ya fijada en `spec.md`/`requirements.md` — ninguno especulativo.

**Extensión deliberada del Playbook, documentada (no silenciosa):** el ejemplo propio del Playbook (Paso 1) es un CRUD de `users` con JWT ya existente como prerrequisito ("estilo REST y JWT ya elegidos... debes tenerlo antes de empezar"). Este proyecto, a diferencia de `01_CRUD`, no puede asumir JWT como un prerrequisito externo: `tasks.md` M2 exige explícitamente "registro, login, refresh" como parte del propio alcance. Se añaden 3 endpoints de autenticación (Feature 1) que el Playbook no ejemplifica literalmente, tratados como las "operaciones reales" que el Paso 1 pide identificar para la entidad Usuario, con el mismo criterio de "ninguno especulativo" — los tres están citados literalmente en `spec.md` Feature 1 y `requirements.md` FR1-FR3.

## Tabla de endpoints (Paso 1)

| Endpoint | Operación real |
|---|---|
| `POST /api/v1/auth/register` | alta de usuario — FR1 |
| `POST /api/v1/auth/login` | autenticación, emite access+refresh — FR2 |
| `POST /api/v1/auth/refresh` | nuevo access_token sin re-autenticar password — FR3 |
| `POST /api/v1/tasks` | alta de tarea propia — FR4 |
| `GET /api/v1/tasks` | listado paginado y filtrado, solo tareas propias — FR4, FR7 |
| `GET /api/v1/tasks/{id}` | detalle — FR4, FR6 (401/403/404) |
| `PUT /api/v1/tasks/{id}` | edición — FR4, FR6 |
| `DELETE /api/v1/tasks/{id}` | soft delete (`eliminado_en`, nunca DELETE físico) — FR4, FR5, FR6 |

`GET /docs` y `GET /openapi.json` (Feature 5, FR9/FR10) no se listan como endpoint de negocio: los genera automáticamente el framework, sin lógica propia, y deben quedar accesibles sin autenticación (FR10) — verificado en el Paso 6.

## Contratos (Paso 2)

### `POST /api/v1/auth/register`
Request: `{"email": str, "password": str}` → **201** `{"id","email"}` | **422** (email con formato inválido, password vacío) | **409** (email ya registrado — FR1 "email único")

### `POST /api/v1/auth/login`
Request: `{"email": str, "password": str}` → **200** `{"access_token","refresh_token","token_type":"bearer"}` | **401** (email o password incorrectos)

### `POST /api/v1/auth/refresh`
Request: `{"refresh_token": str}` → **200** `{"access_token","token_type":"bearer"}` | **401** (refresh_token inválido, expirado, o no es de tipo refresh)

### `POST /api/v1/tasks`
Cabecera: `Authorization: Bearer <access_token>`. Request: `{"titulo": str, "descripcion": str, "estado": str | null}` → **201** `{"id","titulo","descripcion","estado","propietario_id"}` | **400** (`titulo` vacío, `estado` fuera del enum) | **401** (sin token o token inválido)

`estado` es opcional en el request: si se omite, el servicio lo fija a `"pendiente"` — cierra explícitamente el punto abierto que `disenio.md` (M1) dejó sin resolver a nivel de esquema ("ninguna regla fija qué estado recibe una tarea recién creada"); la regla se fija aquí, en la capa de aplicación, no en la base de datos.

### `GET /api/v1/tasks`
Cabecera: `Authorization: Bearer <access_token>`. Query: `?status=&page=&limit=` → **200** `{"items":[...],"total","page","limit"}` (nunca más de `limit` resultados, nunca tareas ajenas ni soft-deleted — FR7) | **401** (sin token o token inválido) | **400** (`status` fuera del enum)

### `GET /api/v1/tasks/{id}`
Cabecera: `Authorization: Bearer <access_token>` → **200** `{"id","titulo","descripcion","estado","propietario_id"}` | **401** (sin token) | **403** (existe pero pertenece a otro usuario — FR6, respuesta genérica sin datos de la tarea, NFR5) | **404** (no existe o está soft-deleted)

### `PUT /api/v1/tasks/{id}`
Cabecera: `Authorization: Bearer <access_token>`. Request: `{"titulo": str, "descripcion": str, "estado": str}` → **200** `{"id","titulo","descripcion","estado","propietario_id"}` | **400** (valor inválido) | **401** | **403** (FR6, NFR5) | **404**

### `DELETE /api/v1/tasks/{id}`
Cabecera: `Authorization: Bearer <access_token>` → **200** `{"id","eliminado_en"}` (soft delete, `UPDATE`, nunca `DELETE` físico — FR5) | **401** | **403** (FR6, NFR5) | **404**

**Regla de precedencia 403 vs. 404, aplicada de forma consistente en los 3 endpoints con `{id}`:** una tarea soft-deleted se trata como inexistente (**404**) para cualquier llamante, incluido su propietario — nunca **403**, para no revelar mediante el código de estado si una tarea ajena fue borrada o nunca existió (extensión razonada de NFR5). Solo una tarea activa (`eliminado_en IS NULL`) que pertenece a otro usuario produce **403**.
