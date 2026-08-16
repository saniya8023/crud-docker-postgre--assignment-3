from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A complete CRUD REST API for managing to-do items built for Week 2 assignment."
)

# --- Stage 2: In-memory Task Storage ---
tasks_db = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Review OOP concepts", "done": True},
    {"id": 3, "title": "Complete Week 2 CRUD API assignment", "done": False}
]

# Data Models using Pydantic (Input Validation)
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# --- Stage 1: Root and Health Endpoints ---
@app.get("/", summary="Root Endpoint")
def get_root():
    """Returns basic API metadata and endpoints."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/health", "/docs", "/stats"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    """Checks whether the server is up and running."""
    return {"status": "ok"}

# --- Extras: Stats Endpoint ---
@app.get("/stats", summary="Get Task Statistics")
def get_stats():
    """Computes total, completed, and open tasks dynamically."""
    total = len(tasks_db)
    done_count = sum(1 for t in tasks_db if t["done"])
    return {
        "total": total,
        "done": done_count,
        "open": total - done_count
    }

# --- Stage 2: Read Endpoints ---
@app.get("/tasks", summary="Get All Tasks")
def get_tasks(
    done: Optional[bool] = Query(None, description="Filter tasks by completion status"),
    search: Optional[str] = Query(None, description="Search tasks by title keyword")
):
    """Retrieves all tasks with optional filtering and search parameters."""
    filtered = tasks_db
    if done is not None:
        filtered = [t for t in filtered if t["done"] == done]
    if search:
        filtered = [t for t in filtered if search.lower() in t["title"].lower()]
    return filtered

@app.get("/tasks/{id}", summary="Get Task by ID")
def get_task(id: int):
    """Retrieves a single task by its unique ID. Returns 404 if not found."""
    task = next((t for t in tasks_db if t["id"] == id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {id} not found"
        )
    return task

# --- Stage 3: Create Endpoint ---
@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create Task")
def create_task(payload: TaskCreate):
    """Creates a new task. Validates that 'title' is non-empty."""
    title_text = payload.title.strip() if payload.title else ""
    if not title_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty or blank."
        )
    
    new_id = max([t["id"] for t in tasks_db], default=0) + 1
    new_task = {
        "id": new_id,
        "title": title_text,
        "done": False
    }
    tasks_db.append(new_task)
    return new_task

# --- Stage 4: Update & Delete Endpoints ---
@app.put("/tasks/{id}", summary="Update Task")
def update_task(id: int, payload: TaskUpdate):
    """Updates an existing task's title and/or completion state."""
    task = next((t for t in tasks_db if t["id"] == id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {id} not found"
        )
    
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must supply title or done state to update."
        )
        
    if payload.title is not None:
        title_text = payload.title.strip()
        if not title_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty."
            )
        task["title"] = title_text
        
    if payload.done is not None:
        task["done"] = payload.done

    return task

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(id: int):
    """Deletes a task by ID. Returns 204 No Content on success."""
    global tasks_db
    task_idx = next((index for index, t in enumerate(tasks_db) if t["id"] == id), None)
    if task_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {id} not found"
        )
    tasks_db.pop(task_idx)
    return None

# --- Extras: Reset Endpoint ---
@app.post("/reset", summary="Reset Database Seed")
def reset_tasks():
    """Resets the task database back to the initial seed state."""
    global tasks_db
    tasks_db.clear()
    tasks_db.extend([
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Review OOP concepts", "done": True},
        {"id": 3, "title": "Complete Week 2 CRUD API assignment", "done": False}
    ])
    return {"status": "Database reset to initial state"}