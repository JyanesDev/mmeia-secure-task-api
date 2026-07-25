from fastapi import FastAPI

from src.routers import auth, tasks

app = FastAPI(title="mmeia-secure-task-api")

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
def health():
    return {"status": "ok"}
