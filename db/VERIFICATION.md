# Schema verification (Playbook Paso 6)

Executed against a real, disposable `postgres:16` container (`docker run -d --rm --name mmeia-task-api-db-verify`), not simulated. Container stopped and removed immediately after (`docker stop`, confirmed with `docker ps -a` showing no matching container).

## 1. Apply schema.sql

```
CREATE TABLE
CREATE TABLE
```

2 tables created without errors, in dependency order (Usuario → Tarea).

## 2. Constraint tests (each expected to fail)

| # | Test | Real result |
|---|---|---|
| 1 | `Usuario.email` duplicado | `ERROR: duplicate key value violates unique constraint "usuario_email_key"` |
| 2 | `Tarea.propietario_id` nulo | `ERROR: null value in column "propietario_id" of relation "tarea" violates not-null constraint` |
| 3 | `Tarea.propietario_id` inexistente | `ERROR: insert or update on table "tarea" violates foreign key constraint "tarea_propietario_id_fkey"` |
| 4 | `Tarea.estado` fuera del enum (`'archivada'`) | `ERROR: new row for relation "tarea" violates check constraint "tarea_estado_check"` |

All 4 failed exactly as `disenio.md` required — none passed silently, none failed for the wrong reason.

## 3. Soft delete verification (`tasks.md` M1, tercera comprobación explícita — más allá de las 3 pruebas mínimas del Playbook)

| Paso | Acción | Resultado real |
|---|---|---|
| 1 | Insertar una Tarea válida | `INSERT 0 1` |
| 2 | Contar filas con ese `id` | `count = 1` |
| 3 | `UPDATE ... SET eliminado_en = now()` (nunca `DELETE`) | `UPDATE 1` |
| 4 | Contar filas con ese `id` de nuevo (la fila debe seguir existiendo) | `count = 1` — confirma que no fue un `DELETE` físico |
| 5 | Contar filas con ese `id` filtrando `WHERE eliminado_en IS NULL` | `count = 0` — confirma que una consulta que solo debe ver tareas activas la excluye correctamente |

Comportamiento exactamente como exige FR5 ("Soft delete... nunca DELETE físico") y la tercera verificación explícita de `tasks.md` M1.

## 4. Estado final

```
          List of relations
 Schema |  Name   | Type  |  Owner
--------+---------+-------+----------
 public | tarea   | table | postgres
 public | usuario | table | postgres
(2 rows)
```

Playbook Checklist final, casilla 7 ("Las pruebas de restricción fallan exactamente como se describe"): satisfecho. Las 3 verificaciones explícitas de `tasks.md` M1 (unicidad de email, FK propietario_id, soft delete) están las tres cubiertas con evidencia real.

**Date:** 2026-07-25. **Engine:** PostgreSQL 16 (official Docker image, `postgres:16`).
