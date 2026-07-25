# Diseño de datos

Producido siguiendo `04_Playbooks/01_Disenar_Base_Datos/PLAYBOOK.md` (Pasos 1-4) de MMEIA. Entidades y reglas ya fijadas en `spec.md`/`requirements.md` y en el alcance de M1 fijado en `tasks.md` (Usuario, Tarea).

## Usuario
- id — identificador único
- email — regla: FR1 "Registro de usuario (email único, password con hash)"
- password_hash — regla: FR1 "password con hash"; NFR3 "Passwords nunca en texto plano, ni en logs ni en respuestas"

## Tarea
- id — identificador único
- titulo — regla: Feature 2 "Cada tarea tiene título, descripción y estado"
- descripcion — regla: Feature 2 "Cada tarea tiene título, descripción y estado"
- estado — regla: Feature 2 "estado (pendiente | en_progreso | completada)"
- propietario_id — regla: FR4 "CRUD de tareas, ownership obligatorio"; `tasks.md` M1 "Verificación de FK propietario_id"
- eliminado_en — regla: FR5 "Soft delete (campo eliminado_en, nunca DELETE físico)"; `tasks.md` M1 "Verificación de soft delete"

No se incluye ninguna tabla para `access_token`/`refresh_token`: `tasks.md` M1 fija explícitamente el alcance de esta base de datos a Usuario y Tarea; los tokens JWT (FR2/FR3/NFR4) son responsabilidad de M2 (`02_Crear_API`) y no requieren almacenamiento propio salvo que M2 decida soportar revocación — decisión explícitamente diferida, no tomada aquí.

---

## Tipos de dato y clave primaria (Paso 2)

- **Usuario:** id (UUID, PK), email (TEXT), password_hash (TEXT)
- **Tarea:** id (UUID, PK), titulo (TEXT), descripcion (TEXT), estado (TEXT), propietario_id (UUID), eliminado_en (TIMESTAMP)

**Decisión de diseño — UUID como tipo de PK:** verificado con `grep` que `spec.md`/`requirements.md`/`tasks.md` no mencionan `UUID` en ningún punto — no es un requisito de la especificación. Es el propio Paso 2 del Playbook el que lo ofrece como convención por defecto ("añade `id (UUID, PK)` si falta identificador natural"), la misma convención ya aplicada en `01_CRUD`. Se adopta por consistencia con el resto del ecosistema, no por una regla de negocio: un entero autoincremental habría sido igualmente válido.

Ningún importe monetario en este dominio — no aplica la comprobación de coma flotante del Paso 2.

## Relaciones y claves foráneas (Paso 3)

- `Tarea.propietario_id → FK Usuario.id` (1:N — un Usuario tiene muchas Tareas)

Sin relaciones N:M en este dominio (alcance fijado por `tasks.md` M1: solo Usuario y Tarea).

## Restricciones desde las reglas de negocio (Paso 4)

- `Usuario.email` → `NOT NULL, UNIQUE` (FR1: "email único")
- `Usuario.password_hash` → `NOT NULL` (FR1 "password con hash"; NFR3: nunca en texto plano — el hash siempre debe existir)
- `Tarea.titulo` → `NOT NULL` (Feature 2: toda tarea tiene título)
- `Tarea.descripcion` → `NOT NULL` — **decisión de diseño, no regla de la spec:** Feature 2 solo exige que el atributo *exista* ("Cada tarea tiene título, descripción y estado"), no que sea obligatorio en cada fila. Se exige `NOT NULL` para simplificar el modelo (la aplicación nunca necesita distinguir "sin descripción" de "descripción vacía"); puede ser cadena vacía, nunca `NULL`. Si se prefiriera permitir ausencia real, bastaría con quitar `NOT NULL` — no hay coste de migración relevante en esta fase.
- `Tarea.estado` → `NOT NULL, CHECK (estado IN ('pendiente', 'en_progreso', 'completada'))` (Feature 2: enumera exactamente estos tres valores)
- `Tarea.propietario_id` → `NOT NULL, REFERENCES Usuario(id) ON DELETE RESTRICT` (FR4 "ownership obligatorio"; `tasks.md` M1 "Verificación de FK propietario_id")
- `Tarea.eliminado_en` → sin `NOT NULL` (nullable): `NULL` = tarea activa, valor no nulo = soft-deleted (FR5: "campo eliminado_en, nunca DELETE físico")

**Decisión de diseño, sin regla explícita que la dicte (registrada aquí, no en `docs/decisions.md`, por ser de alcance puramente estructural):** `Tarea.propietario_id` usa `ON DELETE RESTRICT` en vez de `CASCADE`. Ninguna FR/NFR describe qué ocurre si un Usuario se elimina — de hecho ninguna Feature del alcance actual permite eliminar un Usuario. `RESTRICT` es el valor por defecto más seguro (impide perder Tareas en silencio si esa operación llegara a existir); puede revisarse sin coste si M2 introduce baja de usuarios.

**Punto abierto, explícitamente sin resolver aquí:** `Tarea.estado` no lleva `DEFAULT`. Ninguna regla fija qué estado recibe una tarea recién creada; se deja que la capa de aplicación (M2) lo fije explícitamente en cada `INSERT`, en vez de asumir `'pendiente'` sin una regla que lo respalde.

Ninguna restricción aquí carece de una regla de negocio que la exija (criterio de finalización del Paso 4 del Playbook).
