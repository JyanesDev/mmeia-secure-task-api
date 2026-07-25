# Deployment

## Local (this project's only target — same deliberately small scope as `01_CRUD`)

```bash
cp .env.example .env   # fill in real values first, including a real JWT_SECRET
docker compose -f docker/docker-compose.yml --env-file .env up -d --build
```

Two services: `api` (built from `docker/Dockerfile`) and `db` (official `postgres:16` image, auto-initialized with `db/schema.sql` via `docker-entrypoint-initdb.d`). Connection string, database credentials, and `JWT_SECRET` all via environment variables (`.env`, gitignored; `.env.example` committed with placeholder values) — see `despliegue.md` for the full inventory.

## What is deliberately not here

No Kubernetes manifests, no cloud provider config — this project's scope doesn't justify any of it (`docs/architecture.md`). No secret manager / KMS for `JWT_SECRET` — a single `.env` file is proportionate to a local Docker Compose target; a real production deployment of this API would need one, out of scope here.

## CI

`.github/workflows/ci.yml`: 3 jobs chained with `needs:` — `build` (Docker image, saved as an artifact), `test` (pytest against a real PostgreSQL 16 service container), `deploy` (loads the built image; since this project's declared target is local Docker Compose, not a remote host, "deploy" here means the tested image is the artifact an operator pulls and runs — there is no remote push step).

**Honest limitation:** the workflow's YAML was validated locally (`python -c "import yaml; yaml.safe_load(...)"`) but has not been observed running on a real GitHub Actions runner in this session — same limitation already documented in `01_CRUD`. It will execute for real on the next push to GitHub; if it fails there, that's new evidence to fold in before `v1.0.0`.

## Real deployment evidence (M3, 2026-07-25)

Executed for real, not simulated — `docker compose up -d --build` from a clean `.env`, both containers reached a healthy/running state with no manual steps beyond providing `.env`. Full functional smoke test against the containerized app (register → login) confirmed the stack works end-to-end, not just that the container starts.

Full verification (Playbook `03_Preparar_Despliegue`, Paso 6 — all 5 points, including a genuine 5-minute wait):

```text
1. Disponibilidad     -> GET /health -> 200 {"status":"ok","version":"0.3.0"}
2. Salud               -> mismo endpoint, mismo resultado
3. Version reportada   -> "0.3.0", coincide con la esperada
4. Version anterior    -> mmeia-secure-task-api:0.2.0 presente en `docker images`
                          (reconstruida desde el tag real v0.2.0 via git worktree,
                          usando el Dockerfile actual sobre el código fuente tal
                          como estaba en ese tag - mismo procedimiento ya aplicado
                          en 01_CRUD, para que esta comprobación tenga sustancia
                          real y no sea un cheque vacío)
5. Estabilidad 5 min    -> misma respuesta tras esperar 300s reales (20:30:47 ->
                          20:35:47); contenedores "Up 9 minutes (healthy)" en la
                          comprobación final
```

Playbook Checklist final: 10/10 satisfied.

Ambos contenedores detenidos y eliminados (`docker compose down`) tras completar la verificación — este despliegue local es una demostración reproducible, no un servicio que deba permanecer levantado entre sesiones.
