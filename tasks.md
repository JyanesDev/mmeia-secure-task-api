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
- [x] M3 — Despliegue (03_Preparar_Despliegue): Docker, CI, verificación
      de 5 puntos, igual que 01_CRUD — DONE 2026-07-25
      - `despliegue.md` (Paso 1, incluye JWT_SECRET como secreto además de
        las credenciales de BD), `docker/Dockerfile` (Paso 2, imagen 0.3.0
        construida y verificada funcionalmente en local: register+login
        reales), `.github/workflows/ci.yml` (Paso 3, 3 jobs encadenados,
        YAML validado localmente), `docker/docker-compose.yml` +
        `.env.example` (Paso 4), despliegue real ejecutado (Paso 5:
        `docker compose up -d --build`, ambos contenedores healthy/running),
        verificación de 5 puntos (Paso 6, `docs/deployment.md`): disponibilidad,
        salud, versión coincide (0.3.0), versión anterior presente (0.2.0,
        reconstruida vía git worktree), estabilidad tras 5 minutos reales.
        Playbook Checklist final: 10/10.
- [ ] M4 — Revisión formal, commit_referencia, congelación v1.0.0
