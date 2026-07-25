# Plan de milestones — Task Management API

- [x] M0 — Scaffold del repositorio (estructura, spec/requirements/tasks
      ya versionados desde el commit inicial, no añadidos después)
- [x] M1 — Base de datos (01_Disenar_Base_Datos): Usuario, Tarea — DONE 2026-07-25
      - [x] Verificación de unicidad de email
      - [x] Verificación de FK propietario_id
      - [x] Verificación de soft delete
      - `disenio.md` (Pasos 1-4) y `db/schema.sql` (Paso 5) creados; esquema aplicado y verificado contra un contenedor PostgreSQL 16 real y desechable (`db/VERIFICATION.md`, Paso 6). Playbook Checklist final: 7/7.
- [x] M2 — API (02_Crear_API), esta vez con el Paso 5 (JWT) aplicado
      completo: registro, login, refresh, CRUD con ownership — DONE 2026-07-25
      - [x] Tests explícitos: 401, 403, 404, refresh token, access token
        expirado
      - `api/contrato.md` (Pasos 1-2), estructura de capas (Paso 3),
        endpoints implementados (Paso 4), JWT aplicado a las 5 rutas de
        tareas (Paso 5) y verificación completa (Paso 6, `api/VERIFICATION.md`):
        36 tests de pytest contra PostgreSQL 16 real y desechable + smoke
        test de 12 escenarios contra un servidor `uvicorn` real. 6 ADR-RP
        documentados en `docs/decisions.md`. Playbook Checklist final: 5/5.
- [ ] M3 — Despliegue (03_Preparar_Despliegue): Docker, CI, verificación
      de 5 puntos, igual que 01_CRUD
- [ ] M4 — Revisión formal, commit_referencia, congelación v1.0.0
