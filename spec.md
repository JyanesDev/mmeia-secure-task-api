# Spec — Task Management API

## Feature 1: Registro y autenticación
Un usuario se registra con email/password. Al hacer login recibe un
access_token (JWT, vida corta) y un refresh_token (vida larga).
Puede usar el refresh_token para obtener un access_token nuevo sin
volver a introducir su password.

## Feature 2: Gestión de tareas propias
Un usuario autenticado puede crear, leer, modificar y eliminar
(soft delete) sus propias tareas. Cada tarea tiene título,
descripción y estado (pendiente | en_progreso | completada).

## Feature 3: Ownership y autorización
Un usuario autenticado que intenta acceder a una tarea que no le
pertenece recibe 403, no 401 (ya sabemos quién es, no puede hacer
esto) y nunca ve datos de la tarea ajena en la respuesta. Esta es
la tesis central del proyecto: no basta con saber quién eres, el
sistema debe decidir qué puedes hacer.

## Feature 4: Listado con paginación y filtrado
GET /api/v1/tasks admite ?status=, ?page=, ?limit= — nunca devuelve
más de `limit` resultados, nunca tareas de otro usuario.

## Feature 5: Contrato y documentación viva
La API expone automáticamente una especificación OpenAPI actualizada
que refleja el estado real del sistema. La documentación debe
permanecer sincronizada con el código en todo momento y servir como
contrato único entre cliente y servidor.
