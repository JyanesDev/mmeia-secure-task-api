# Inventario de configuración y secretos

Producido siguiendo `04_Playbooks/03_Preparar_Despliegue/PLAYBOOK.md` (Paso 1). Búsqueda de literales ejecutada dos veces sobre `src/` (`grep -rn "os.environ"` y una relectura manual archivo por archivo) — sin hallazgos nuevos en la segunda pasada.

DATABASE_URL (secreto) — cadena de conexión completa a PostgreSQL, distinta en cada entorno
POSTGRES_USER (secreto)
POSTGRES_PASSWORD (secreto)
POSTGRES_DB (no secreto, nombre de la base de datos)
JWT_SECRET (secreto) — clave de firma de los JWT (access y refresh); a diferencia de `01_CRUD`, este proyecto sí tiene un secreto de aplicación además de las credenciales de base de datos — es la tesis central del proyecto, por lo que su tratamiento como secreto real (nunca el valor de desarrollo por defecto de `src/security.py`) es especialmente importante
APP_PORT (no secreto, valor por defecto 8000)

Entorno de destino de este proyecto (mismo alcance deliberadamente local que `01_CRUD`, `tasks.md` M3: "igual que 01_CRUD"): Docker Compose en la propia máquina, no una plataforma cloud. Ningún literal hardcodeado quedó en `src/` tras la segunda búsqueda: `src/database.py` ya lee `DATABASE_URL` de una variable de entorno (`os.environ.get(...)`, con valor por defecto solo para desarrollo local sin Docker); `src/security.py` ya lee `JWT_SECRET` de una variable de entorno con el mismo patrón — el valor por defecto de ambos está marcado explícitamente en el propio código como "dev-only"/"never use in production" (ver `api/VERIFICATION.md`, hallazgo de M2 sobre la longitud del secreto).
