# Requisitos — Task Management API

## Funcionales
FR1. Registro de usuario (email único, password con hash).
FR2. Login -> access_token (JWT) + refresh_token.
FR3. Refresh -> nuevo access_token sin re-autenticar password.
FR4. CRUD de tareas, ownership obligatorio.
FR5. Soft delete (campo eliminado_en, nunca DELETE físico).
FR6. 401 si no autenticado; 403 si autenticado pero no propietario;
     404 si el recurso no existe.
FR7. Listado paginado y filtrable por estado.
FR8. Contrato versionado en /api/v1.
FR9. OpenAPI generado automáticamente desde el framework.
FR10. La documentación OpenAPI debe estar accesible sin autenticación.

## No funcionales
NFR1. Ningún endpoint de tareas es accesible sin JWT válido.
NFR2. Los tests deben probar explícitamente los tres casos de la
      tríada 401/403/404 (no solo el camino feliz).
NFR3. Passwords nunca en texto plano, ni en logs ni en respuestas.
NFR4. Los access_token deben tener una vida inferior a la de los
      refresh_token.
NFR5. Ninguna respuesta 403 debe revelar información suficiente
      para inferir la existencia de recursos ajenos.

## Alcance explícito (IN / OUT)
IN:  JWT, access+refresh tokens, ownership, soft delete, versionado
     en path, paginación, filtrado, OpenAPI.
OUT: RBAC, OAuth social, multi-tenant/organizaciones, API Keys,
     webhooks, rate limiting, SSO.
