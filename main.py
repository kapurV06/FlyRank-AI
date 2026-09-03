from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import db

app = FastAPI()


@app.on_event("startup")
def on_startup():
    # Connect using DATABASE_URL, create the table if missing,
    # seed three example tasks only if the table is empty.
    db.init_db()


@app.get("/")
def root():
    return {"name": "Task API", "version": "3.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok", "db": "ok" if db.ping() else "down"}


@app.get("/tasks")
def get_tasks():
    return db.get_all_tasks()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = db.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


class TaskCreate(BaseModel):
    title: str


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    return db.create_task(task.title)


class TaskUpdate(BaseModel):
    title: str
    done: bool


@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    if not update.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    task = db.update_task(task_id, update.title, update.done)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    deleted = db.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return
