from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List
import sqlite3

app = FastAPI(
    title="Task CRUD API (SQLite)",
    version="2.0",
    description="Week 3 Assignment: SQLite-backed RESTful CRUD API."
)

DB_FILE = "tasks.db"

# --- Database Helper Function ---
def get_db_connection():
    """Creates a connection to SQLite DB with Row factory for dict-like access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Stage 0: Create Database Table & Initial Seed Data ---
def init_db():
    """Initializes schema and seeds initial example tasks if table is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    
    # Check if empty and seed initial data
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        initial_tasks = [
            ("Buy groceries", False),
            ("Review OOP concepts", True),
            ("Connect CRUD to SQLite database", False)
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks)
        conn.commit()
        
    conn.close()

# Run database initialization at startup
init_db()

# --- Pydantic Request Models ---
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# --- Stage 1 & Root Endpoints ---
@app.get("/", summary="Root Endpoint")
def get_root():
    return {
        "name": "Task API (SQLite Engine)",
        "version": "2.0",
        "endpoints": ["/tasks", "/health", "/stats"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok", "database": "connected"}

@app.get("/stats", summary="Get Statistics using SQL COUNT()")
def get_stats():
    """Executes SQL aggregate functions to compute statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
    done_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total": total,
        "done": done_count,
        "open": total - done_count
    }

# --- Stage 1: Read Endpoints ---
@app.get("/tasks", summary="List All Tasks with SQL Filtering")
def get_tasks(
    done: Optional[bool] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, description="Search keyword using SQL LIKE")
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params = []
    
    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)
        
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    tasks = [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        for row in rows
    ]
    return tasks

@app.get("/tasks/{id}", summary="Get Task by ID")
def get_task(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {id} not found"
        )
        
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

# --- Stage 2: Create Endpoint ---
@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Insert Task into Database")
def create_task(payload: TaskCreate):
    title_text = payload.title.strip() if payload.title else ""
    if not title_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty."
        )
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (title_text,))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return {"id": new_id, "title": title_text, "done": False}

# --- Stage 3: Update & Delete Endpoints ---
@app.put("/tasks/{id}", summary="Update Task Row")
def update_task(id: int, payload: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check existence
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
    existing = cursor.fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {id} not found"
        )
        
    if payload.title is None and payload.done is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must supply title or done state to update."
        )
        
    new_title = existing["title"]
    new_done = existing["done"]
    
    if payload.title is not None:
        stripped = payload.title.strip()
        if not stripped:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty."
            )
        new_title = stripped
        
    if payload.done is not None:
        new_done = 1 if payload.done else 0
        
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, id)
    )
    conn.commit()
    conn.close()
    
    return {"id": id, "title": new_title, "done": bool(new_done)}

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task Row")
def delete_task(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {id} not found"
        )
        
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return None