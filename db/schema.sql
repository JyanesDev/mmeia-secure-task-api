-- Generated per 04_Playbooks/01_Disenar_Base_Datos/PLAYBOOK.md (Paso 5), from disenio.md.
-- Order: Usuario (no dependencies) -> Tarea (references Usuario).

CREATE TABLE Usuario (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE Tarea (
    id UUID PRIMARY KEY,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    estado TEXT NOT NULL
        CHECK (estado IN ('pendiente', 'en_progreso', 'completada')),
    propietario_id UUID NOT NULL REFERENCES Usuario(id) ON DELETE RESTRICT,
    eliminado_en TIMESTAMP
);
