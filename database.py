import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@db:5432/taskdb")

def get_db_connection():
    """Establishes connection to PostgreSQL with retry logic for container startup delay."""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            time.sleep(2)
    raise Exception("Could not connect to PostgreSQL database.")

def fetch_all_tasks(done=None, search=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params = []
    
    if done is not None:
        query += " AND done = %s"
        params.append(done)
    if search:
        query += " AND title ILIKE %s"
        params.append(f"%{search}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_task_by_id(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def insert_task(title: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, false) RETURNING id, title, done", (title,))
    new_task = cursor.fetchone()
    conn.commit()
    conn.close()
    return new_task

def update_task_record(task_id: int, title: str = None, done: bool = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        return None
        
    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]
    
    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
        (new_title, new_done, task_id)
    )
    updated_task = cursor.fetchone()
    conn.commit()
    conn.close()
    return updated_task

def delete_task_record(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
    if not cursor.fetchone():
        conn.close()
        return False
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return True

def fetch_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM tasks")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as done FROM tasks WHERE done = true")
    done_count = cursor.fetchone()["done"]
    conn.close()
    return {"total": total, "done": done_count, "open": total - done_count}