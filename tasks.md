# Plan de milestones — Task Management API

- [x] M0 — Scaffold del repositorio (estructura, spec/requirements/tasks
      ya versionados desde el commit inicial, no añadidos después)
- [ ] M1 — Base de datos (01_Disenar_Base_Datos): Usuario, Tarea
      - Verificación de unicidad de email
      - Verificación de FK propietario_id
      - Verificación de soft delete
- [ ] M2 — API (02_Crear_API), esta vez con el Paso 5 (JWT) aplicado
      completo: registro, login, refresh, CRUD con ownership
      - Tests explícitos: 401, 403, 404, refresh token, access token
        expirado
- [ ] M3 — Despliegue (03_Preparar_Despliegue): Docker, CI, verificación
      de 5 puntos, igual que 01_CRUD
- [ ] M4 — Revisión formal, commit_referencia, congelación v1.0.0
