# Decisions (ADR log)

Decisiones reales tomadas durante M1-M2, con sus alternativas descartadas y su justificación — mismo criterio que `01_CRUD` (`ADR-001`-`ADR-003`). Un ADR aquí documenta una decisión que este proyecto tomó de verdad, con al menos una alternativa que seguía viva en el momento de decidir — no una restricción que la especificación ya había cerrado antes de empezar (ver la nota al final de este documento para esos casos).

## ADR-RP01 — JWT frente a sesiones con estado

**Status:** Accepted.

**Context:** la API necesita identificar al llamante en cada petición, sin acoplarse a un almacenamiento de sesión compartido.

**Alternatives:**
- (a) Sesiones con estado (cookie + almacén server-side: Redis, tabla de sesiones).
- (b) JWT sin estado, firmado, verificado en cada petición sin consultar la base de datos.

**Decision:** (b).

**Rationale:** el alcance explícito (`requirements.md` IN) fija JWT desde el diseño; además, una API sin estado de sesión no necesita invalidar nada en un almacén compartido para verificar identidad — el coste es no poder revocar un token individual antes de su expiración (aceptado, ver `ADR-RP03`).

**Consequences:** ningún endpoint de tareas consulta la base de datos para validar la identidad del llamante, solo para autorización (ownership) — la verificación de la firma y expiración del JWT es suficiente y se hace en memoria (`src/deps.py`).

## ADR-RP02 — 401 vs. 403 como conceptos distintos, nunca intercambiables

**Status:** Accepted.

**Context:** `FR6` exige distinguir "no autenticado" de "autenticado pero no autorizado".

**Alternatives:**
- (a) Un único código (401) para ambos casos, dejando que el cliente infiera la causa por el mensaje.
- (b) 401 solo cuando falta o es inválido el token; 403 solo cuando el token es válido pero el recurso pertenece a otro usuario.

**Decision:** (b).

**Rationale:** esta distinción es la tesis central del proyecto (`spec.md` Feature 3): "ya sabemos quién eres, no puedes hacer esto" es una afirmación distinta de "no sabemos quién eres". Un cliente (o un atacante) que reciba siempre 401 no puede distinguir un fallo de autenticación de un fallo de autorización, lo que dificulta tanto el debugging legítimo como el modelado de amenazas.

**Consequences:** `src/deps.py` (verificación de token) y `src/services.py` (`obtener_autorizada`) son dos puntos de fallo completamente separados en el código — nunca se comparte lógica entre "token inválido" y "no eres el propietario".

## ADR-RP03 — Access + Refresh Tokens, sin rotación de refresh_token

**Status:** Accepted.

**Context:** `FR2`/`FR3` exigen renovar el `access_token` sin pedir la contraseña de nuevo; `NFR4` exige que el `access_token` expire antes que el `refresh_token`.

**Alternatives:**
- (a) Un único token de larga duración.
- (b) Access token de vida corta (15 min) + refresh token de vida larga (7 días), sin rotación: `POST /refresh` siempre devuelve el mismo tipo de respuesta, nunca emite un refresh_token nuevo.
- (c) Como (b), pero con rotación: cada `POST /refresh` invalida el refresh_token usado y emite uno nuevo.

**Decision:** (b).

**Rationale:** (a) viola `NFR4` directamente. (c) exige una lista de revocación (tabla de refresh tokens usados/vigentes) que `tasks.md` M1 no incluyó en el alcance de la base de datos — introducirla ahora habría sido "adelantar trabajo no pedido" (mismo criterio ya aplicado en M1 al no crear una tabla de tokens). (b) cumple `NFR4` sin estado adicional; el coste es que un refresh_token robado sigue siendo válido hasta su expiración natural (7 días) — riesgo aceptado explícitamente, no analizado en profundidad porque excede el alcance de este proyecto (rate limiting y revocación están en `requirements.md` OUT).

**Consequences:** ambos tokens son JWT firmados con el mismo secreto pero un claim `"type"` distinto (`"access"` / `"refresh"`); `src/services.py` (`AuthService.refrescar`) rechaza explícitamente cualquier token cuyo `type` no sea `"refresh"`, evitando que un access_token robado se use para obtener otro access_token indefinidamente.

## ADR-RP04 — Soft delete: `eliminado_en` tratado como ausencia total del recurso, no un estado visible

**Status:** Accepted.

**Context:** `FR5` exige soft delete (`eliminado_en`, nunca `DELETE` físico); no especifica qué debe ver un usuario que consulta una tarea ya borrada.

**Alternatives:**
- (a) Devolver la tarea igualmente (200), marcada como borrada en el body.
- (b) Tratar cualquier tarea con `eliminado_en` no nulo como si no existiera (`404`) para cualquier llamante, incluido su propio dueño.

**Decision:** (b).

**Rationale:** (a) obligaría a cada cliente a comprobar un campo adicional en cada respuesta para saber si una tarea sigue "viva" — una fuente de bugs si se olvida. (b) mantiene el contrato simple: una tarea o existe (activa) o no existe (soft-deleted o nunca creada), sin un tercer estado ambiguo expuesto por la API. Extiende además `NFR5` por analogía: si una tarea ajena ya borrada devolviera `403` en vez de `404`, un atacante podría inferir que existió.

**Consequences:** `TareaRepository.obtener_activa` es el único punto de lectura por id de toda la capa de servicio — ninguna consulta a una tarea individual puede "olvidar" filtrar `eliminado_en IS NULL`, porque no existe otro método para hacerlo.

---

## Restricciones ya fijadas por la especificación (no ADR)

Los dos puntos siguientes se registraron inicialmente como `ADR-RP05`/`ADR-RP06`. Revisados a petición explícita del usuario antes del commit de M2: ninguno de los dos documenta una decisión tomada por este proyecto — ambos ya venían cerrados por `requirements.md` antes de M1/M2, sin ninguna alternativa realmente viva en el momento de construir. Mantenerlos como "ADR" habría sido presentar una restricción recibida como si fuera una decisión de ingeniería propia — degradados aquí a nota, sin numeración ADR-RP, para no diluir el criterio de qué cuenta como ADR real (los 4 anteriores sí lo son).

**Versionado en path (`/api/v1`), no en cabecera.** Fijado por `requirements.md` IN ("versionado en path") antes de que existiera código. Razón general documentada por completitud: un prefijo de ruta es visible en cualquier log de acceso o prueba manual con `curl` sin que el cliente añada nada a la petición, más simple de operar que una cabecera personalizada.

**Ownership como modelo de autorización, no RBAC.** Fijado por `requirements.md` (RBAC está explícitamente en OUT) antes de que existiera código. `TareaService.obtener_autorizada` es una comprobación de igualdad simple (`tarea.propietario_id == usuario_id`), sin ningún camino de excepción (rol, flag de admin) en el código — consistente con que RBAC nunca fue una opción abierta en este proyecto, no con que se haya evaluado y descartado aquí.
