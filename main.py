from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional
import database as db

app = FastAPI(title="Task CRUD API (Dockerized Postgres)", version="3.0")

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def root():
    return {"name": "Task API", "engine": "PostgreSQL in Docker", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "database": "connected"}

@app.get("/stats")
def stats():
    return db.fetch_stats()

@app.get("/tasks")
def get_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    return db.fetch_all_tasks(done=done, search=search)

@app.get("/tasks/{id}")
def get_task(id: int):
    task = db.fetch_task_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    title = payload.title.strip() if payload.title else ""
    if not title:
        raise HTTPException(status_code=400, detail="Task title cannot be empty.")
    return db.insert_task(title)

@app.put("/tasks/{id}")
def update_task(id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Must supply title or done state.")
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(status_code=400, detail="Task title cannot be empty.")
    
    updated = db.update_task_record(id, payload.title, payload.done)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    success = db.delete_task_record(id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None