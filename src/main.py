from fastapi import FastAPI

from src.routers import auth, tasks

# Bumped on each deployment milestone (03_Preparar_Despliegue, Paso 6 punto 3:
# "consulta la version reportada por la app y comparala con la esperada").
APP_VERSION = "0.3.0"

app = FastAPI(title="mmeia-secure-task-api", version=APP_VERSION)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}
