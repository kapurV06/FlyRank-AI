from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

import db
from auth import supabase, get_current_user

app = FastAPI()


@app.on_event("startup")
def on_startup():
    # Connect using DATABASE_URL, create the table if missing,
    # seed three example tasks only if the table is empty.
    db.init_db()


@app.get("/")
def root():
    return {"name": "Task API", "version": "4.0", "endpoints": ["/tasks", "/auth", "/public", "/protected"]}


@app.get("/health")
def health():
    return {"status": "ok", "db": "ok" if db.ping() else "down"}


# ---------------------------------------------------------------------
# A3 — tasks (unchanged)
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# A4 — auth (new)
# ---------------------------------------------------------------------

class AuthCredentials(BaseModel):
    email: str
    password: str


@app.post("/auth/signup", status_code=201)
def signup(creds: AuthCredentials):
    if not creds.email.strip() or not creds.password.strip():
        raise HTTPException(status_code=400, detail="email and password are required")
    try:
        result = supabase.auth.sign_up(
            {"email": creds.email, "password": creds.password}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user": result.user}


@app.post("/auth/login")
def login(creds: AuthCredentials):
    if not creds.email.strip() or not creds.password.strip():
        raise HTTPException(status_code=400, detail="email and password are required")
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": creds.email, "password": creds.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
    }


@app.post("/auth/logout", status_code=204)
def logout(user=Depends(get_current_user)):
    supabase.auth.sign_out()
    return


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile")
def profile(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}


@app.get("/protected/dashboard")
def dashboard(user=Depends(get_current_user)):
    # Same guard, second door — nothing new to write.
    return {"message": f"Welcome back, {user.email}"}
