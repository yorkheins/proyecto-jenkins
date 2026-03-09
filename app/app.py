from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI(
    title="DevOps Demo App",
    description="API REST de tareas para practicar pipelines CI/CD con Jenkins",
    version="1.0.0",
)

# "Base de datos" en memoria
tasks: list[dict] = [
    {"id": 1, "title": "Aprender Jenkins", "done": False},
    {"id": 2, "title": "Configurar pipeline CI/CD", "done": False},
    {"id": 3, "title": "Desplegar en producción", "done": False},
]
next_id = 4


# --- Schemas ---

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


# --- Endpoints ---

@app.get("/")
def index():
    return {
        "app": "DevOps Demo App",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(body: TaskCreate):
    global next_id
    new_task = {"id": next_id, "title": body.title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, body: TaskUpdate):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    if body.title is not None:
        task["title"] = body.title
    if body.done is not None:
        task["done"] = body.done
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tasks = [t for t in tasks if t["id"] != task_id]
    return {"message": "Tarea eliminada"}
